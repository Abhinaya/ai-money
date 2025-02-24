async function getBaseUrl(): Promise<string> {
    return `${window.location.host}/api`;
}

export async function getBaseHttpUrl(): Promise<string> {
    return `${window.location.protocol}//${await getBaseUrl()}`;
}

export async function getBaseWsUrl(): Promise<string> {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${wsProtocol}//${await getBaseUrl()}`;
}
