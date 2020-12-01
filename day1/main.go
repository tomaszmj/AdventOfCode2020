package main

import (
	"errors"
	"fmt"
	"io"
	"os"
)

func main() {
	data, err := readData("data1.txt")
	if err != nil {
		fmt.Println(err)
		return
	}
	solve1(data)
	solve2(data)
}

func solve1(data []int) {
	// Brute-force - possible as there is little data
	for i := 0; i < len(data) - 1; i++ {
		for j := i + 1; j < len(data); j++ {
			if data[i] + data[j] == 2020 {
				fmt.Printf("Answer1: %d\n", data[i] * data[j])
				return
			}
		}
	}
	fmt.Println("Could not find 2 numbers that sum up to 2020")
}

func solve2(data []int) {
	// Brute-force - possible as there is little data
	for i := 0; i < len(data) - 2; i++ {
		for j := i + 1; j < len(data) - 1; j++ {
			for k := j + 1; k < len(data); k++ {
				if data[i] + data[j] + data[k] == 2020 {
					fmt.Printf("Answer2: %d\n", data[i] * data[j] * data[k])
					return
				}
			}
		}
	}
	fmt.Println("Could not find 3 numbers that sum up to 2020")
}

func readData(filename string) ([]int, error) {
	f, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	data := make([]int, 0)
	for {
		var n int
		_, err = fmt.Fscanf(f, "%d", &n)
		if errors.Is(err, io.EOF) {
			return data, nil
		} else if err != nil {
			return nil, err
		}
		data = append(data, n)
	}
}