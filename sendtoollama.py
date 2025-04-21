import requests
import json

def send_to_ollama(prompt, model_name):
    url = "http://localhost:11434/api/generate"
    payload = {
        "prompt": prompt,
        "model": model_name,
        "stream": False
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json().get('response', '') # Return the generated text
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        if response is not None:
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
        return None

# Example of how you might call it from your GUI:
if __name__ == "__main__":
    # Simulate getting prompt and model from your GUI
    test_prompt = "What is the weather like in Paris?"
    test_model = "Qwen2.5:7b"
    ollama_response = send_to_ollama(test_prompt, test_model)
    if ollama_response:
        print(f"Ollama Response: {ollama_response}")