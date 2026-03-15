import asyncio
import sys
import os
import argparse
from playwright.async_api import async_playwright

async def generate_vheer_image(prompt, output_file="vheer_output.png", user_data_dir=None, headless=True):
    """
    Automates image generation on vheer.com using Playwright.
    """
    async with async_playwright() as p:
        print(f"🚀 Starting Vheer Automation...")
        if user_data_dir:
            context = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=headless,
                viewport={'width': 1280, 'height': 800}
            )
        else:
            browser = await p.chromium.launch(headless=headless)
            context = await browser.new_context(viewport={'width': 1280, 'height': 800})
            
        page = await context.new_page()
        
        try:
            print(f"🌐 Navigating to Vheer Text-to-Image...")
            await page.goto("https://vheer.com/app/text-to-image", wait_until="networkidle", timeout=60000)
            
            print(f"✍️ Typing prompt: \"{prompt}\"")
            # Wait for textarea and fill it
            await page.wait_for_selector("textarea", timeout=15000)
            await page.fill("textarea", prompt)
            
            print(f"🔘 Clicking Generate...")
            generate_button = page.locator("button:has-text('Generate')")
            await generate_button.wait_for(state="visible", timeout=10000)
            await generate_button.click()
            
            print(f"⏳ Processing image (this can take up to 90s)...")
            
            # Use a more reliable way to detect completion: 
            # 1. The button text changes to 'Generate' again (after being 'Loading...')
            # 2. Or the image with alt='selected image' appears/updates
            
            # Wait for 'Processing...' to appear and then disappear, or just wait for the image result.
            await page.wait_for_selector("img[alt='selected image']", timeout=120000)
            
            # Small buffer to ensure rendering is complete
            await asyncio.sleep(2)
            
            print(f"✅ Image Generated!")
            
            # Click the download button and wait for the download
            print(f"📥 Downloading original image...")
            download_button_selector = "div.absolute.top-3.right-3.inline-flex button:first-child"
            
            async with page.expect_download() as download_info:
                await page.click(download_button_selector)
            
            download = await download_info.value
            # Save to the specified output path
            await download.save_as(output_file)
            
            abs_path = os.path.abspath(output_file)
            print(f"💾 Image saved successfully to: {abs_path}")
            return abs_path
                
        except Exception as e:
            print(f"❌ Error during generation: {str(e)}")
            return None
        finally:
            await context.close()
            if not user_data_dir:
                await browser.close()

def main():
    parser = argparse.ArgumentParser(description="Vheer AI Image Generation Automation")
    parser.add_argument("prompt", type=str, help="The text prompt to generate an image from")
    parser.add_argument("-o", "--output", type=str, default="vheer_output.png", help="Output filename (default: vheer_output.png)")
    parser.add_argument("--headful", action="store_true", help="Run browser in headful mode (visible)")
    parser.add_argument("--user-data", type=str, help="Path to user data directory for persistent session")

    args = parser.parse_args()

    if not args.prompt:
        print("Error: Please provide a prompt.")
        sys.exit(1)

    try:
        asyncio.run(generate_vheer_image(
            prompt=args.prompt,
            output_file=args.output,
            user_data_dir=args.user_data,
            headless=not args.headful
        ))
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
