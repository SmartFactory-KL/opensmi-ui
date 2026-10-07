async function simplyGet(url: string): Promise<Response> {
  const result = await fetch(url);
  if (!result.ok) {
    let resultText = "";

    try {
      resultText = await result.text();
    } catch (e) {
      resultText = "could not convert result";
    }

    throw new Error(
      `GET ${url} failed: ${result.status} ${result.statusText} ${resultText}`,
    );
  }

  return result;
}

async function simplyPost(url: string, data: any): Promise<Response> {
  const result = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  if (!result.ok) {
    let resultText = "";

    try {
      resultText = await result.text();
    } catch (e) {
      resultText = "could not convert result";
    }

    throw new Error(
      `POST ${url} failed: ${result.status} ${result.statusText} ${resultText}`,
    );
  }

  return result;
}

export async function simplyGetToJSON(url: string): Promise<any> {
  const result = await simplyGet(url);
  return await result.json();
}

export async function simplyGetToText(url: string): Promise<string> {
  const result = await simplyGet(url);
  return await result.text();
}

export async function simplyPostToJSON(url: string, data: any): Promise<any> {
  const result = await simplyPost(url, data);
  return await result.json();
}

export async function simplyPostToText(url: string, data: any): Promise<string> {
  const result = await simplyPost(url, data);
  return await result.text();
}
