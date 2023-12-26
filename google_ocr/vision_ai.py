import pickle

def detect_text(path, output_path):
    """Detects text in the file."""
    from google.cloud import vision

    client = vision.ImageAnnotatorClient()

    with open(path, "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    # print(response)
    # print(response.text_annotations)

    texts = response.text_annotations
    with open(output_path, 'w') as f:
        f.write('description,bottomleft,bottomright,topright,topleft\n')
        for text in texts:
            # print(text)
            description = text.description.replace('\n', '\\n').replace('"', '""')
            # print(description)
            f.write(f'"{description}",')
            for idx, vertex in enumerate(text.bounding_poly.vertices):
                # print(vertex)
                if idx == len(text.bounding_poly.vertices) - 1:
                    f.write(f'"({vertex.x},{vertex.y})"\n')
                else:
                    f.write(f'"({vertex.x},{vertex.y})",')

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )

