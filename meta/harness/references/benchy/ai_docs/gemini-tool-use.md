[![Gemini API](https://ai.google.dev/_static/googledevai/images/lockup-new.svg)](/)

`/`

- English
- Deutsch
- Español – América Latina
- Français
- Indonesia
- Italiano
- Polski
- Português – Brasil
- Tiếng Việt
- Türkçe
- Русский
- עברית
- العربيّة
- فارسی
- हिंदी
- বাংলা
- ภาษาไทย
- 中文 – 简体
- 中文 – 繁體
- 日本語
- 한국어

Sign in

Grounding with Google Search is now available! [Learn more](https://developers.googleblog.com/en/gemini-api-and-ai-studio-now-offer-grounding-with-google-search)

- [Home](https://ai.google.dev/)
- [Gemini API](https://ai.google.dev/gemini-api)
- [Docs](https://ai.google.dev/gemini-api/docs)



 Send feedback



# Function calling tutorial


 Stay organized with collections


 Save and categorize content based on your preferences.


PythonNode.jsGoDart (Flutter)AndroidSwiftWebREST

Function calling makes it easier for you to get structured data outputs from
generative models. You can then use these outputs to call other APIs and return
the relevant response data to the model. In other words, function calling helps
you connect generative models to external systems so that the generated content
includes the most up-to-date and accurate information.

You can provide Gemini models with descriptions of functions. These are
functions that you write in the language of your app (that is, they're not
Google Cloud Functions). The model may ask you to call a function and send back
the result to help the model handle your query.

If you haven't already, check out the
[Introduction to function calling](/gemini-api/docs/function-calling) to learn
more. You can also
try out this feature in
[Google Colab](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Function_calling_config.ipynb)
or view the example code in the
[Gemini API Cookbook](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling_config.ipynb) repository.

## Example API for lighting control

Imagine you have a basic lighting control system with an application programming
interface (API) and you want to allow users to control the lights through simple
text requests. You can use the Function Calling feature to interpret lighting
change requests from users and translate them into API calls to set the lighting
values. This hypothetical lighting control system lets you control the
brightness of the light and it's color temperature, defined as two separate
parameters:

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `brightness` | number | yes | Light level from 0 to 100. Zero is off and 100 is full brightness. |
| `colorTemperature` | string | yes | Color temperature of the light fixture which can be `daylight`, `cool` or `warm`. |

For simplicity, this imaginary lighting system only has one light, so the user
does not have to specify a room or location. Here is an example JSON request
you could send to the lighting control API to change the light level to 50%
using the daylight color temperature:

```
{
  "brightness": "50",
  "colorTemperature": "daylight"
}

```

This tutorial shows you how to set up a Function Call for the Gemini API to
interpret users lighting requests and map them to API settings to control a
light's brightness and color temperature values.

## Before you begin: Set up your project and API key

Before calling the Gemini API, you need to set up your project and configure
your API key.

**Expand to view how to set up your project and API key**

### Get and secure your API key

You need an API key to call the Gemini API. If you don't already have one,
create a key in Google AI Studio.

[Get an API key](https://aistudio.google.com/app/apikey)

It's strongly recommended that you do _not_ check an API key into your version
control system.

You should store your API key in a secrets store such as Google Cloud
[Secret Manager](https://cloud.google.com/secret-manager/docs).

This tutorial assumes that you're accessing your API key as an environment
variable.

### Install the SDK package and configure your API key

The Python SDK for the Gemini API is contained in the
[`google-generativeai`](https://pypi.org/project/google-generativeai/) package.

1. Install the dependency using pip:


```
pip install -U google-generativeai

```

2. Import the package and configure the service with your API key:


```
import os
import google.generativeai as genai

genai.configure(api_key=os.environ['API_KEY'])

```


## Define an API function

Create a function that makes an API request. This function should be defined
within the code of your application, but could call services or APIs outside of
your application. The Gemini API does _not_ call this function directly, so you
can control how and when this function is executed through your application
code. For demonstration purposes, this tutorial defines a mock API function that
just returns the requested lighting values:

```
def set_light_values(brightness, color_temp):
    """Set the brightness and color temperature of a room light. (mock API).

    Args:
        brightness: Light level from 0 to 100. Zero is off and 100 is full brightness
        color_temp: Color temperature of the light fixture, which can be `daylight`, `cool` or `warm`.

    Returns:
        A dictionary containing the set brightness and color temperature.
    """
    return {
        "brightness": brightness,
        "colorTemperature": color_temp
    }

```

When you create a function to be used in a function call by the model, you
should include as much detail as possible in the function and parameter
descriptions. The generative model uses this information to determine which
function to select and how to provide values for the parameters in the function
call.

## Declare functions during model initialization

When you want to use function calling with a model, you must declare your
functions when you initialize the model object. You declare functions by setting
the model's `tools` parameter:

```
model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                              tools=[set_light_values])

```

## Generate a function call

Once you have initialized model with your function declarations, you can prompt
the model with the defined function. You should use function calling using
chat prompting ( `sendMessage()`), since function calling generally benefits from
having the context of previous prompts and responses.

```
chat = model.start_chat()
response = chat.send_message('Dim the lights so the room feels cozy and warm.')
response.text

```

The Python SDK's
[`ChatSession`](https://ai.google.dev/api/python/google/generativeai/ChatSession)
object simplifies managing chat sessions by handling the conversation history
for you. You can use the `enable_automatic_function_calling` to have the SDK
automatically call the function.

```
# Create a chat session that automatically makes suggested function calls
chat = model.start_chat(enable_automatic_function_calling=True)

```

## Parallel function calling

In addition to basic function calling described above, you can also call multiple functions in a single turn. This section shows an example for how you can use parallel function calling.

Define the tools.

```
def power_disco_ball(power: bool) -> bool:
    """Powers the spinning disco ball."""
    print(f"Disco ball is {'spinning!' if power else 'stopped.'}")
    return True

def start_music(energetic: bool, loud: bool, bpm: int) -> str:
    """Play some music matching the specified parameters.

    Args:
      energetic: Whether the music is energetic or not.
      loud: Whether the music is loud or not.
      bpm: The beats per minute of the music.

    Returns: The name of the song being played.
    """
    print(f"Starting music! {energetic=} {loud=}, {bpm=}")
    return "Never gonna give you up."

def dim_lights(brightness: float) -> bool:
    """Dim the lights.

    Args:
      brightness: The brightness of the lights, 0.0 is off, 1.0 is full.
    """
    print(f"Lights are now set to {brightness:.0%}")
    return True

```

Now call the model with an instruction that could use all of the specified tools.

```
# Set the model up with tools.
house_fns = [power_disco_ball, start_music, dim_lights]

model = genai.GenerativeModel(model_name="gemini-1.5-flash", tools=house_fns)

# Call the API.
chat = model.start_chat()
response = chat.send_message("Turn this place into a party!")

# Print out each of the function calls requested from this single call.
for part in response.parts:
    if fn := part.function_call:
        args = ", ".join(f"{key}={val}" for key, val in fn.args.items())
        print(f"{fn.name}({args})")

```

```
power_disco_ball(power=True)
start_music(energetic=True, loud=True, bpm=120.0)
dim_lights(brightness=0.3)

```

Each of the printed results reflects a single function call that the model has requested. To send the results back, include the responses in the same order as they were requested.

```
# Simulate the responses from the specified tools.
responses = {
    "power_disco_ball": True,
    "start_music": "Never gonna give you up.",
    "dim_lights": True,
}

# Build the response parts.
response_parts = [\
    genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn, response={"result": val}))\
    for fn, val in responses.items()\
]

response = chat.send_message(response_parts)
print(response.text)

```

```
Let's get this party started! I've turned on the disco ball, started playing some upbeat music, and dimmed the lights. 🎶✨  Get ready to dance! 🕺💃

```

## Function call data type mapping

Automatic schema extraction from Python functions doesn't work in all cases. For example: it doesn't handle cases where you describe the fields of a nested dictionary-object, but the API does support this. The API is able to describe any of the following types:

```
AllowedType = (int | float | bool | str | list['AllowedType'] | dict[str, AllowedType])

```

The [google.ai.generativelanguage](https://ai.google.dev/api/python/google/generativeai/protos) client library provides access to the low level types giving you full control.

First peek inside the model's `_tools` attribute, you can see how it describes the function(s) you passed it to the model:

```
def multiply(a:float, b:float):
    """returns a * b."""
    return a*b

model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                             tools=[multiply])

model._tools.to_proto()

```

```
[function_declarations {\
   name: "multiply"\
   description: "returns a * b."\
   parameters {\
     type_: OBJECT\
     properties {\
       key: "b"\
       value {\
         type_: NUMBER\
       }\
     }\
     properties {\
       key: "a"\
       value {\
         type_: NUMBER\
       }\
     }\
     required: "a"\
     required: "b"\
   }\
 }]

```

This returns the list of `genai.protos.Tool` objects that would be sent to the
API. If the printed format is not familiar, it's because these are Google
protobuf classes. Each `genai.protos.Tool` (1 in this case) contains a list of
`genai.protos.FunctionDeclarations`, which describe a function and its
arguments.

Here is a declaration for the same multiply function written using the
`genai.protos` classes. Note that these classes just describe the function for
the API, they don't include an implementation of it. So using this doesn't work
with automatic function calling, but functions don't always need an
implementation.

```
calculator = genai.protos.Tool(
    function_declarations=[\
      genai.protos.FunctionDeclaration(\
        name='multiply',\
        description="Returns the product of two numbers.",\
        parameters=genai.protos.Schema(\
            type=genai.protos.Type.OBJECT,\
            properties={\
                'a':genai.protos.Schema(type=genai.protos.Type.NUMBER),\
                'b':genai.protos.Schema(type=genai.protos.Type.NUMBER)\
            },\
            required=['a','b']\
        )\
      )\
    ])

```

Equivalently, you can describe this as a JSON-compatible object:

```
calculator = {'function_declarations': [\
      {'name': 'multiply',\
       'description': 'Returns the product of two numbers.',\
       'parameters': {'type_': 'OBJECT',\
       'properties': {\
         'a': {'type_': 'NUMBER'},\
         'b': {'type_': 'NUMBER'} },\
       'required': ['a', 'b']} }]}

```

```
genai.protos.Tool(calculator)

```

```
function_declarations {
  name: "multiply"
  description: "Returns the product of two numbers."
  parameters {
    type_: OBJECT
    properties {
      key: "b"
      value {
        type_: NUMBER
      }
    }
    properties {
      key: "a"
      value {
        type_: NUMBER
      }
    }
    required: "a"
    required: "b"
  }
}

```

Either way, you pass a representation of a `genai.protos.Tool` or list of tools to

```
model = genai.GenerativeModel('gemini-1.5-flash', tools=calculator)
chat = model.start_chat()

response = chat.send_message(
    f"What's 234551 X 325552 ?",
)

```

Like before the model returns a `genai.protos.FunctionCall` invoking the calculator's `multiply` function:

```
response.candidates

```

```
[index: 0\
content {\
  parts {\
    function_call {\
      name: "multiply"\
      args {\
        fields {\
          key: "b"\
          value {\
            number_value: 325552\
          }\
        }\
        fields {\
          key: "a"\
          value {\
            number_value: 234551\
          }\
        }\
      }\
    }\
  }\
  role: "model"\
}\
finish_reason: STOP\
]

```

Execute the function yourself:

```
fc = response.candidates[0].content.parts[0].function_call
assert fc.name == 'multiply'

result = fc.args['a'] * fc.args['b']
result

```

```
76358547152.0

```

Send the result to the model, to continue the conversation:

```
response = chat.send_message(
    genai.protos.Content(
    parts=[genai.protos.Part(\
        function_response = genai.protos.FunctionResponse(\
          name='multiply',\
          response={'result': result}))]))

```



 Send feedback



Except as otherwise noted, the content of this page is licensed under the [Creative Commons Attribution 4.0 License](https://creativecommons.org/licenses/by/4.0/), and code samples are licensed under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0). For details, see the [Google Developers Site Policies](https://developers.google.com/site-policies). Java is a registered trademark of Oracle and/or its affiliates.

Last updated 2024-11-14 UTC.


Need to tell us more?


\[\[\["Easy to understand","easyToUnderstand","thumb-up"\],\["Solved my problem","solvedMyProblem","thumb-up"\],\["Other","otherUp","thumb-up"\]\],\[\["Missing the information I need","missingTheInformationINeed","thumb-down"\],\["Too complicated / too many steps","tooComplicatedTooManySteps","thumb-down"\],\["Out of date","outOfDate","thumb-down"\],\["Samples / code issue","samplesCodeIssue","thumb-down"\],\["Other","otherDown","thumb-down"\]\],\["Last updated 2024-11-14 UTC."\],\[\],\[\]\]
