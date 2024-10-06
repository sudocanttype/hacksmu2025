from openai import OpenAI
import base64
import json

client = OpenAI(api_key=os.environ.get("GPT_KEY")


def c1(file)
    encoded_string = ""
    with open(file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())




    img_type = "image/jpeg"
    encoded_string = str(encoded_string)[2:-1]

    if len(encoded_string) == 0:
        pass
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "You are given an image of a parking spot. \
                    Identify any obstructions in the parking spot that should not be there. \
                    Return results as a JSON dictionary with the fields 'license', 'obstructions'.\
                    If the spot has a car, return the license plate.\
                    Otherwise, return the obstructions if there are any.\
                    "},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{img_type};base64,{encoded_string}",
                        }
                    },
                ],
            }
        ],
    )
    a = json.loads(completion.choices[0].message.content[8:-4])

    print(a)

    return a
