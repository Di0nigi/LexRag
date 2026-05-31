export async function sendChatMessage(query) {


  const urlPrefix = "https://starlit-ship-octopus.ngrok-free.dev";
  const response = await fetch(urlPrefix+"/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: query,
      top_k: 5,
      filters: null,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch response");
  }

  return await response.json();
}

