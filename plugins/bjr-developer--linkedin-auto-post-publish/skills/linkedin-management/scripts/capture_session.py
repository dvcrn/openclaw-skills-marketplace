import asyncio
import json
from playwright.async_api import async_playwright

async def capture_linkedin_session():
    async with async_playwright() as p:
        # Launch headed browser so the user can interact
        browser = await p.chromium.launch(headless=False)
        
        # Use a persistent context to keep things if needed, or just a new one
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Dictionary to store interesting requests
        captured_requests = []

        async def handle_request(request):
            # Capture LinkedIn API calls and graphql calls
            if "linkedin.com" in request.url:
                # We want to capture POST requests or api calls
                if request.method == "POST" or "api" in request.url or "graphql" in request.url:
                    try:
                        capture = {
                            "url": request.url,
                            "method": request.method,
                            "headers": request.headers,
                            "post_data": request.post_data
                        }
                        captured_requests.append(capture)
                        print(f"Captured: {request.method} {request.url[:100]}...")
                    except Exception as e:
                        print(f"Error capturing request: {e}")

        page.on("request", handle_request)

        print("Opening LinkedIn... Please log in and then create a post, comment, and like manually.")
        await page.goto("https://www.linkedin.com/")

        print("The browser is open. Please:")
        print("1. Log in (if not already).")
        print("2. Create a test post.")
        print("3. Like a post.")
        print("4. Comment on a post.")
        print("\nDO NOT CLOSE THE BROWSER MANUALLY.")
        print("I will wait 5 minutes for you to complete this, or you can signal me.")
        
        try:
            # We wait either for manual enter or a long timeout
            await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(None, input, "Press Enter here in the console when you have finished interacting: "),
                timeout=300 # 5 minutes
            )
        except asyncio.TimeoutError:
            print("Timeout reached, saving whatever we captured...")

        # Save cookies
        cookies = await context.cookies()
        with open("linkedin_cookies.json", "w") as f:
            json.dump(cookies, f, indent=4)
        
        # Save captured requests for analysis
        with open("linkedin_network_log.json", "w") as f:
            json.dump(captured_requests, f, indent=4)

        print("\n" + "="*30)
        print("Session saved to linkedin_cookies.json")
        print("Network log saved to linkedin_network_log.json")
        print("="*30)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_linkedin_session())
