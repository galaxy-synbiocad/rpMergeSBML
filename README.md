# Merge SBML

Merge two SBML's

## Getting Started

This is a docker galaxy tools, and thus, the docker needs to be built locally where Galaxy is installed. 

## Input

Required information:
* **-target_sbml**: (string) Path to either tar.xz input collection of SBML files or a single SBML file.
* **-input**: (string) Path to the input file
* **-input_format**: (string) Format of the input (tar or sbml)

## Output

* **output**: (string) Path to the tar or sbml output

## Installing

To build the image using the Dockerfile, use the following command:

```
docker build -t brsynth/rpmergesbml-standalone .
```

### Running the tests

To run the test, untar the test.tar.xz file and run the following command:

```
python run,py -input test/source_model.sbml -input_format sbml -target_sbml target.sbml -output test/test_output.sbml
```

## Prerequisites

* Base Docker Image: [python:3.6](https://hub.docker.com/_/python)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

v0.1

## Authors

* **Melchior du Lac**

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thomas Duigou
* Joan Hérisson

### How to cite rpOptBioDes?
