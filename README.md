## 0. Contents

- [Introduction](#Introduction)
- [API Endpoints](#API%20Endpoints)
- [Request Parameters](#Request%20Parameters)
- [Response Formats](#Response%20Formats)
- [Installation and examples](#Installation%20and%20examples)
- [Contributing](#Contributing)
- [License and Terms](#License%20and%20Terms)

## Introduction

Access and explore Christopher Alexander's _A Pattern Language_ through a RESTful API.

This API extends zenodotus280's [patternlanguage.cc](https://patternlanguage.cc) project, using markdown files from the [apl-md repository](https://github.com/zenodotus280/apl-md). Parsed and structured with [FastAPI](https://fastapi.tiangolo.com) as the back-end, the API offers a structured way to interact with _A Pattern Language_, enabling programmatic access to its patterns.

- **Overview**: The API provides searchable access to the patterns in _A Pattern Language_, allowing users to query by ID, name, tag, and other parameters.
- **Target Audience**: Researchers, developers, and enthusiasts of Christopher Alexander's work.
- **Use Cases**: Integrating pattern details into other applications, using patterns as part of a project’s MOTD, finding patterns based on their page number, etc..

## API Endpoints

| HTTP Method | Endpoint URL                 | Description                                           | Request Format | Response Format |
|-------------|-------------------------------|-------------------------------------------------------|----------------|-----------------|
| GET         | `/id/{id}`                    | Retrieves pattern by ID                               | JSON           | JSON            |
| GET         | `/name/{pattern_name}`        | Retrieves pattern by name                             | JSON           | JSON            |
| GET         | `/find/{name}`                | Searches patterns by partial name                     | JSON           | JSON            |
| GET         | `/page_number/{page_number}`  | Finds closest pattern based on page number            | JSON           | JSON            |
| GET         | `/confidence/{confidence}`    | Retrieves patterns by confidence level                | JSON           | JSON            |
| GET         | `/tag/{tag}`                  | Finds patterns by associated tag                      | JSON           | JSON            |

## Request Parameters

| Parameter Name | Type   | Description                             | Required |
| -------------- | ------ | --------------------------------------- | -------- |
| `id`           | int    | Unique ID of the pattern                | Yes      |
| `pattern_name` | string | Full name of the pattern                | Yes      |
| `page_number`  | int    | Page number to find the closest pattern | Yes      |
| `confidence`   | int    | Confidence level of the pattern         | Yes      |
| `tag`          | string | Tag associated with the pattern         | No       |
| `depth`        | int    | Depth level for related links (max = 3) | No       |
>[!note]
>The confidence parameter only accepts values between `1` and `3`, inclusive. These integers correspond to the confidence value:
>`1` -> low confidence
>`2` -> medium confidence
>`3` -> high confidence

## Response Formats

- **Format**: JSON
- **Response Structure**:
  ```json
{
  "id": 253,
  "name": "Things From Your Life",
  "problem": "“Decor” and the conception of “interior design” have spread so widely, that very often people forget their instinct for the things they really want to keep around them.",
  "solution": "Do not be tricked into believing that modern decor must be slick or psychedelic, or “natural” or \"modern art\", or “plants” or anything else that current taste-makers claim. It is most beautiful when it comes straight from your life—the things you care for, the things that tell your story.",
  "page_number": 1164,
  "confidence": 2,
  "tag": "apl/construction-patterns/ornamentation",
  "forward_links": [],
  "backlinks": [
    {
      "id": 141,
      "name": "A Room Of One'S Own",
      "problem": "No one can be close to others, without also having frequent opportunities to be alone.",
      "solution": "Give each member of the family a room of their own, especially adults. A minimum room of one’s own is an alcove with a desk, shelves, and curtain. The maximum is a cottage—like a [[Teenager's Cottage (154)]] , or an [[Old Age Cottage (155)]]. In all cases, especially the adult ones, place these rooms at the far ends of the intimacy gradient—far from the common rooms.",
      "page_number": 668,
      "confidence": 3,
      "tag": "apl/building-patterns/private-rooms",
      "forward_links": [],
      "backlinks": []
    },
    {
      "id": 201,
      "name": "Waist-High Shelf",
      "problem": "In every house and every workplace there is a daily “traffic” of the objects which are handled most. Unless such things are immediately at hand, the flow of life is awkward, full of mistakes; things are forgotten, misplaced.",
      "solution": "Build waist-high shelves around at least a part of the main rooms where people live and work. Make them long, 9 to 15 inches deep, with shelves or cupboard underneath. Interrupt the shelf for seats, windows, and doors.",
      "page_number": 922,
      "confidence": 1,
      "tag": "apl/building-patterns/thick-walls",
      "forward_links": [],
      "backlinks": []
    },
    {
      "id": 249,
      "name": "Ornament",
      "problem": "All people have the instinct to decorate their surroundings.",
      "solution": "Search around the building, and find those edges and transitions which need emphasis or extra binding energy. Corners, places where materials meet, door frames, windows, main entrances, the place where one wall meets another, the garden gate, a fence—all these are natural places which call out for ornament.\nNow find simple themes and apply the elements of the theme over and over again to the edges and boundaries which you decide to mark. Make the ornaments work as seams along the boundaries and edges so that they knit the two sides together and make them one.",
      "page_number": 1146,
      "confidence": 3,
      "tag": "apl/construction-patterns/ornamentation",
      "forward_links": [],
      "backlinks": []
    }
  ]
}
  ```

## Installation and examples

The easiest way to run this API is to use [Docker](https://www.docker.com/). Clone this repository with the following command:

```bash
git clone https://github.com/adnanvaldes/apl-api.git
```

Then go into the `apl-api` directory and run the Docker build command to create a Docker image:

```bash
cd apl-api
docker build -t apl_api .
```

*Note: you can name the container image whatever you want; in this case, we are naming the image `apl_api`. Also, notice the period `.` at the end of the command.*

Once build, you can run the image with:

```bash
docker run -d --name apl_api -p 8000:80 apl_api
```

If everything went well, you should have access to the docs at https://localhost:8000

### With cURL:

```bash
curl -X 'GET' \
  'http://localhost:8934/id/{id}?pattern_id=253&depth=1' \
  -H 'accept: application/json'
```

###  With Python
```python
import requests


response = requests.get("http://localhost:8000/id/1")
print(response.json())


response = requests.get("http://localhost:8000/find/magic")
print(response.json())
```

###  With JavaScript
```javascript
fetch("http://localhost:8000/id/1")
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error("Error:", error));
```

## Contributing

- **Open Issues**: Feel free to check the GitHub repository for open issues.
- **Contribution Guidelines**: Contributions are welcome! Please submit pull requests for new features or bug fixes.
- **Contact**: Reach out via GitHub Issues for questions or feature requests.

## License and Terms

- **License**: MIT License - see `LICENSE` file for details.
- **Terms of Use**: Open-source and free for educational and non-commercial use.
- **Disclaimer**: No warranties or guarantees are provided with this software.