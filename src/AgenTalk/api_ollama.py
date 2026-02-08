import re

from . import util
import ollama,json

OllamaModule=ollama

def GetJsonFromOllama(prompt,model,callback=None):
    if callback is None:
        response=ollama.chat(model=model,messages=[{'role':'user','content':prompt}])
        content=response['message']['content'].strip()
    else:
        stream=ollama.chat(model=model,messages=[{'role':'user','content':prompt}],stream=True)
        s=[]
        for chunk in stream:
            delta=chunk.get('message',{}).get('content','')
            if delta:
                s.append(delta)
                callback(delta)
        content="".join(s)

    jsonStr=util.getJsonStr(content)
    if jsonStr is None:
        util.raiseValueError("No JSON object found in model output.")
    jsonData=json.loads(jsonStr)
    return jsonData

def Summarize(text:str,hint:str='',model='gemma3')->str:
    keyName='summary'
    prompt=f"""
Summarize the following text in one or two sentences. Output only in this JSON format:
{hint}

{{
  "{keyName}": "<concise summary here>"
}}

Do not include any explanation or introductory text. Only return the JSON.

text:
\"\"\"
{text}
\"\"\"
"""
    jsonData=GetJsonFromOllama(prompt)
    if keyName not in jsonData:
        util.raiseValueError(f"key '{keyName}' not found.")
    summary=jsonData[keyName].strip()
    return summary

def TranslateToJa(text:str, hint:str='', model:str='gemma3')->str:
    """
    Translates the given text to Japanese using a local LLM via Ollama.
    Ensures output is structured as JSON to avoid extra commentary.

    Args:
        text (str): The source text to translate.
        model (str): The model name registered in Ollama.
        hint (str): Optional instruction to influence translation style or tone.

    Returns:
        str: The translated Japanese text extracted from the JSON output.
    """
    prompt=(
        "あなたは高精度な翻訳AIです。以下の英文を日本語に翻訳し、"
        "JSON形式で出力してください（キーは 'translation' のみ）。"
    )
    if hint:
        prompt += f" 翻訳のスタイルに関して、次の指示を考慮してください：{hint}"
    keyName='translation'
    prompt += f"\n\n{text}\n\n出力例: {{\"{keyName}\": \"...\"}}"

    jsonData=GetJsonFromOllama(prompt)
    if keyName not in jsonData:
        util.raiseValueError(f"key '{keyName}' not found.")
    return jsonData[keyName].strip()

