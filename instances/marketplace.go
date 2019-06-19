/*
  This golang script uses the marketplace API to retrieve the identifiers of a public image.

  An image is respresented by several identifiers:

  * the marketplace image ID: for example, Ubuntu bionic has only one identifier in the marketplace image.
  * a version ID: for example, everytime Scaleway releases a new version of Ubuntu bionic, a new version is created.
    This version has also an identifier.
  * a local image id: a given version has several identifiers, for example the latest released version of Ubuntu bionic
	has an identifier for x86_64 servers in Paris, another one for arm64 servers in Paris, another one for x86_64
	servers in Amsterdam...

  The local image id is the one you should provide when creating a new server.

  Run the script with --help to get usage.

  Dependencies:

    - linkheader ; install with
        `go get "github.com/tomnomnom/linkheader"`

  To build:

    $. go build marketplace.go && ./marketplace
*/

package main

import "encoding/json"
import "flag"
import "fmt"
import "io/ioutil"
import "net/http"
import "os"
import "regexp"

import "github.com/tomnomnom/linkheader"

type MarketplaceLocalImage struct {
	Id   string `json:"id"`
	Arch string `json:"arch"`
	Zone string `json:"zone"`
}

type MarketplaceImageVersion struct {
	Id          string                  `json:"id"`
	LocalImages []MarketplaceLocalImage `json:"local_images"`
}

type MarketplaceImage struct {
	Id       string                    `json:"id"`
	Name     string                    `json:"name"`
	Versions []MarketplaceImageVersion `json:"versions"`
}

type MarketplaceImageResponse struct {
	Images []MarketplaceImage `json:"images"`
}

// GetNextPageUrl takes a Scaleway paginated API response as parameter and
// returns the next page URL if there is one.
func GetNextPageUrl(resp *http.Response) string {
	for k, v := range resp.Header {
		switch k {
		case "Link":
			links := linkheader.Parse(v[0])
			for _, link := range links {
				switch link.Rel {
				case "next":
					return link.URL
				}
			}
			break
		}
	}
	return ""
}

func ListImages(arch string, name string) ([]MarketplaceImage, error) {

	var ret = []MarketplaceImage{}

	baseUrl := "https://api-marketplace.scaleway.com"
	path := "/images?only_current=true&arch=" + arch

	nameRegex := regexp.MustCompile(`(?i)` + name)

	for {
		// API call
		resp, err := http.Get(baseUrl + path)
		if err != nil {
			return nil, err
		}

		// Read content
		responseBody, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			return nil, err
		}

		// Unmarshal JSON
		var images MarketplaceImageResponse
		if err = json.Unmarshal(responseBody, &images); err != nil {
			return nil, err
		}

		// Iterate over images in response, and append to ret
		for _, image := range images.Images {
			if name == "" {
				ret = append(ret, image)
			} else if match := nameRegex.FindString(image.Name); match != "" {
				ret = append(ret, image)
			}
		}

		// Consume pagination
		path = GetNextPageUrl(resp)
		if path == "" {
			break
		}
	}
	return ret, nil
}

func DisplayImage(image MarketplaceImage, arch string) {
	fmt.Printf("Image %s — %s\n", image.Id, image.Name)

	for _, version := range image.Versions {
		fmt.Printf("  Version identifier: %s\n", version.Id)

		for _, localImage := range version.LocalImages {
			if arch == localImage.Arch {
				fmt.Printf("    Image identifier for %s servers in %s: %s\n", localImage.Arch, localImage.Zone, localImage.Id)
			}
		}
	}
}

func main() {
	arch := flag.String("arch", "x86_64", "Architecture (x86_64, arm64 or arm)")
	name := flag.String("name", "", "Name of the image to search")

	flag.Parse()

	switch *arch {
	case "arm", "arm64", "x86_64":
		break
	default:
		fmt.Fprintf(os.Stderr, "-arch only accepts x86_64 (default), arm64 or arm\n")
		os.Exit(1)
	}

	images, err := ListImages(*arch, *name)
	if err != nil {
		fmt.Fprintf(os.Stderr, "%v\n", err)
		os.Exit(1)
	}

	for _, image := range images {
		DisplayImage(image, *arch)
	}

}
