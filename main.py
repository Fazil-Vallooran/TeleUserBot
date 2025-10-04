import os
import io
import asyncio
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto
from PIL import Image, ImageDraw, ImageFont
import config as cfg

app = TelegramClient('Telethon_UserBot', cfg.API_ID, cfg.API_HASH) # type: ignore

# Track processed messages to prevent loops
processed_ids = set()

def add_watermark(image_bytes: bytes, watermark_text: str) -> bytes:
    """Adds a semi-transparent watermark slightly above bottom-right."""
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    font_size = max(20, image.width // 20)
    try:
        font = ImageFont.truetype("Franklin Gothic Heavy Regular.ttf", font_size)
    except Exception as e:
        print("Failed to load custom font, using default:", e)
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Slightly above bottom-right
    x = image.width - text_width - 10
    y = image.height - text_height - 30

    draw.text((x + 2, y + 2), watermark_text, font=font, fill=(0, 0, 0, 120))  # shadow
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 160))      # semi-transparent

    watermarked = Image.alpha_composite(image, txt_layer)
    output = io.BytesIO()
    watermarked.convert("RGB").save(output, format="JPEG")
    output.seek(0)
    return output.read()

@app.on(events.NewMessage(outgoing=True))
async def on_my_message(event):
    global processed_ids

    if event.message.id in processed_ids:
        return
    processed_ids.add(event.message.id)

    # Determine username for watermark/footer
    channel_username = "@unknown"
    if event.is_channel and event.chat and event.chat.username:
        channel_username = "@" + event.chat.username
    elif event.is_private and (await event.get_sender()).bot:
        sender = await event.get_sender()
        if sender.username:
            channel_username = "@" + sender.username

    # -----------------------------
    # 1️⃣ Handle MP3 / document messages
    # -----------------------------
    if event.message.media and hasattr(event.message.media, "document"):
        file_name = None
        for attr in event.message.media.document.attributes:
            if hasattr(attr, "file_name"):
                file_name, _ = os.path.splitext(attr.file_name)
                # Append filename to message text
                try:
                    await event.message.edit(f"**🎵 {file_name}**\n**🆔 {channel_username}**", parse_mode="md")
                except Exception as e:
                    print("Could not edit MP3 message:", e)
        return  # Stop further processing for MP3/document

    # -----------------------------
    # 2️⃣ Handle channel/bot text messages (append username footer)
    # -----------------------------
    if event.is_channel or (event.is_private and (await event.get_sender()).bot):
        existing_text = event.message.text or ""
        footer = f"\n**━━━━━━━━━━━━━━**\n**🆔 {channel_username}**"
        if footer.strip() not in existing_text:
            try:
                await event.message.edit(existing_text + footer, parse_mode="md")
            except:
                pass

    # -----------------------------
    # 3️⃣ Handle image messages
    # -----------------------------
    if event.message.media and isinstance(event.message.media, MessageMediaPhoto):
        try:
            # Download and watermark
            image_bytes = await event.message.download_media(file=bytes)
            watermarked_bytes = add_watermark(image_bytes, channel_username)
            watermarked_io = io.BytesIO(watermarked_bytes)
            watermarked_io.name = "image.jpg"

            # Preserve caption and append username footer
            caption_text = event.message.text or ""
            footer = f"\n**🆔 {channel_username}**"
            if footer.strip() not in caption_text:
                caption_text += footer

            # Delete original image
            try:
                await event.message.delete()
                await asyncio.sleep(0.3)
            except Exception as e:
                print("Could not delete original image:", e)

            # Send watermarked image
            sent = await event.client.send_file(
                event.chat_id,
                watermarked_io,
                caption=caption_text or None,
                force_document=False
            )
            processed_ids.add(sent.id)

        except Exception as e:
            print("Image processing failed:", e)

if __name__ == "__main__":
    try:
        print("App Started")
        app.start(phone=cfg.PHONE, password=cfg.TWO_STEP_PASS)
        app.run_until_disconnected()
    except KeyboardInterrupt:
        print("App Finished")
