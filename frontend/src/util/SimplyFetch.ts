export function simplyGet(url: string) {
  return fetch(url)
    .then(async (result) => {
      if (!result.ok) {
        let resultText = "";

        try {
          resultText = await result.text();
        } catch (e) {
          resultText = "could not convert result";
        }

        throw new Error(
          `GET ${url} failed: ${result.status} ${result.statusText} ${resultText}`
        );
      }
      return result;
    })
    .then((result) => result.json());
}

export function simplyGetText(url: string) {
  return fetch(url)
    .then(async (result) => {
      if (!result.ok) {
        let resultText = "";

        try {
          resultText = await result.text();
        } catch (e) {
          resultText = "could not convert result";
        }

        throw new Error(
          `GET ${url} failed: ${result.status} ${result.statusText} ${resultText}`
        );
      }
      return result;
    })
    .then((result) => result.text());
}

export function simplyPost(url: string, data: any) {
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
    .then(async (result) => {
      if (!result.ok) {
        let resultText = "";

        try {
          resultText = await result.text();
        } catch (e) {
          resultText = "could not convert result";
        }

        throw new Error(
          `POST ${url} failed: ${result.status} ${result.statusText} ${resultText}`
        );
      }
      return result;
    })
    .then((result) => result.json());
}
