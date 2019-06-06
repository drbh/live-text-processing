package main

import (
	"fmt"
	"github.com/otiai10/gosseract"
	"time"

	// "reflect"
	// "bytes"
	// "image/png"
	// "io/ioutil"
	"regexp"

	b64 "encoding/base64"

	zmq "github.com/pebbe/zmq4"
)

// var content, _ = ioutil.ReadFile("/Users/drbh2/go/src/github.com/otiai10/gosseract/test/data/001-helloworld.png")

var regex = regexp.MustCompile(`\bx[\d]+ .*\b`)

func zmqLoop(f fnct) {
	//  Prepare our subscriber
	subscriber, err := zmq.NewSocket(zmq.SUB)

	if err != nil {
		fmt.Println("CON Error:", err)
	}

	defer subscriber.Close()

	// wait a second - incase the isse is connecting
	// to qickly after opening the socket (suggested on StackOverflow)
	time.Sleep(500 * time.Millisecond)

	// subscriber.Connect("tcp://*:5555")
	subscriber.Connect("tcp://localhost:6748")
	subscriber.SetSubscribe("")

	for {
		// Read envelope with address
		content, err := subscriber.Recv(0)

		if err != nil {
			fmt.Println("MSG Error:", err)

		}
		// d := []byte(address)
		d, _ := b64.StdEncoding.DecodeString(content)
		// fmt.Println(d)
		f(d)
	}
}

// type fnct func(string)
type fnct func([]byte) string

func myfn3(i string) {
	fmt.Printf("\n%s", i)
}

func getText(imagedata []byte) string {
	client := gosseract.NewClient()
	defer client.Close()
	// client.SetImage("screen.png")
	client.SetImageFromBytes(imagedata)
	text, _ := client.Text()

	matches := regex.FindAllString(text, -1)
	fmt.Println("\n")
	for i, v := range matches {
		fmt.Printf("match %2d: '%s'\n", i+1, v)
	}
	return text
}

func main() {

	client := gosseract.NewClient()
	defer client.Close()
	client.SetImage("screen.png")
	text, _ := client.Text()
	fmt.Println(text)

	zmqLoop(getText)

}
