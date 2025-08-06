import logging
import asyncio
import requests
import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

from config import TELEGRAM_TOKEN, PRODUCT_SHOT_TYPES, TEXT_CONTENT_TYPES, WATERMARK_POSITIONS
from api_client import FalAPIClient
from watermark import WatermarkProcessor

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
CHOOSING_OPTION, CHOOSING_SHOT_TYPE, CHOOSING_TEXT_TYPE, WAITING_FOR_TEXT_PROMPT, CHOOSING_WATERMARK_POSITION, ASKING_WATERMARK = range(6)

class ContentCreatorBot:
    def __init__(self):
        self.api_client = FalAPIClient()
        self.watermark_processor = WatermarkProcessor()
        self.user_data = {}  # Store user data temporarily
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        welcome_message = """
🎨 **Content Creator Bot** خوش آمدید!

برای شروع، لطفاً تصویر محصول خود را ارسال کنید.
        """
        await update.message.reply_text(welcome_message, parse_mode=ParseMode.MARKDOWN)
    
    async def handle_image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming product images and show options."""
        user_id = update.message.from_user.id
        
        # Get the largest photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Get file info to get the file URL
        file = await context.bot.get_file(file_id)
        file_url = file.file_path
        
        # Clear any previous conversation state and store the new image URL
        self.user_data[user_id] = {"image_url": file_url}
        
        # Send confirmation message
        await update.message.reply_text(
            "✅ تصویر جدید دریافت شد! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:"
        )
        
        # Create inline keyboard for main options
        keyboard = [
            [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
            [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
            [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup
        )
        
        return CHOOSING_OPTION
    
    async def handle_option_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user's choice between product image or text content."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "product_image":
            # Preserve the image URL if it exists
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            # Show product shot type options
            keyboard = []
            for shot_id, shot_info in PRODUCT_SHOT_TYPES.items():
                keyboard.append([InlineKeyboardButton(shot_info["name"], callback_data=f"shot_{shot_id}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً نوع شات محصول را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_SHOT_TYPE
            
        elif query.data == "text_content":
            # Preserve the image URL if it exists
            if user_id not in self.user_data:
                self.user_data[user_id] = {}
            
            # Show text content type options
            keyboard = []
            for content_type in TEXT_CONTENT_TYPES:
                keyboard.append([InlineKeyboardButton(content_type, callback_data=f"text_{content_type}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً نوع محتوای متنی را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_TEXT_TYPE
        
        elif query.data == "back_to_main":
            # Go back to main menu
            keyboard = [
                [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
                [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
                [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_OPTION
        
        elif query.data == "watermark":
            # Show watermark position options
            keyboard = []
            for pos_id, pos_info in WATERMARK_POSITIONS.items():
                keyboard.append([InlineKeyboardButton(pos_info["name"], callback_data=f"watermark_{pos_id}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً موقعیت واترمارک را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_WATERMARK_POSITION
        
        elif query.data == "back_to_start":
            # Clean up user data and go back to start
            user_id = query.from_user.id
            if user_id in self.user_data:
                del self.user_data[user_id]
            
            await query.edit_message_text(
                "🎨 **Content Creator Bot** خوش آمدید!\n\nبرای شروع، لطفاً تصویر محصول خود را ارسال کنید.",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
    
    async def handle_shot_type_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle product shot type selection and generate image."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Handle back button
        if query.data == "back_to_main":
            # Go back to main menu
            keyboard = [
                [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
                [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_OPTION
        
        shot_id = query.data.replace("shot_", "")
        
        if shot_id in PRODUCT_SHOT_TYPES:
            shot_info = PRODUCT_SHOT_TYPES[shot_id]
            image_url = self.user_data.get(user_id, {}).get("image_url")
            
            if not image_url:
                await query.edit_message_text("❌ خطا: تصویر محصول یافت نشد. لطفاً دوباره تصویر را ارسال کنید.")
                return ConversationHandler.END
            
            # Show processing message
            await query.edit_message_text("🔄 در حال تولید تصویر محصول... لطفاً صبر کنید.")
            
            try:
                # Call the API
                result = await self.api_client.generate_product_image(
                    image_url=image_url,
                    shot_type=shot_info["prompt"]
                )
                
                # Debug: Log the result
                logger.info(f"API Result: {result}")
                
                if result and result.get("images") and len(result["images"]) > 0:
                    # Store the generated image URL for watermarking
                    generated_image_url = result["images"][0]["url"]
                    logger.info(f"Generated image URL: {generated_image_url}")
                    
                    # Store the generated image URL in user data
                    if user_id not in self.user_data:
                        self.user_data[user_id] = {}
                    self.user_data[user_id]["generated_image_url"] = generated_image_url
                    self.user_data[user_id]["shot_info"] = shot_info
                    
                    try:
                        # Download the image first
                        response = requests.get(generated_image_url, timeout=30)
                        response.raise_for_status()
                        
                        # Create a file-like object from the image data
                        image_data = io.BytesIO(response.content)
                        image_data.name = f"generated_image_{shot_id}.jpg"
                        
                        # Send the image as a file
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=image_data,
                            caption=f"✅ تصویر {shot_info['name']} تولید شد!"
                        )
                        success = True
                        
                    except Exception as img_error:
                        logger.error(f"Error downloading/sending image: {img_error}")
                        # If downloading fails, send the URL as text
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"✅ تصویر {shot_info['name']} تولید شد!\n\n🔗 لینک تصویر: {generated_image_url}"
                        )
                        success = True
                else:
                    logger.warning(f"No valid result from API: {result}")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ خطا در تولید تصویر. لطفاً دوباره تلاش کنید."
                    )
                    success = False
                    
            except Exception as e:
                logger.error(f"Error generating product image: {e}")
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ خطا در تولید تصویر. لطفاً دوباره تلاش کنید."
                )
                success = False
            
            # Add a small delay to ensure image is sent first
            import asyncio
            await asyncio.sleep(1)
            
            # Ask if user wants to add watermark
            keyboard = [
                [InlineKeyboardButton("✅ بله، واترمارک اضافه کن", callback_data="watermark_yes")],
                [InlineKeyboardButton("❌ نه، همین کافی است", callback_data="watermark_no")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user_id,
                text="🔒 آیا می‌خواهید واترمارک به این تصویر اضافه کنید؟",
                reply_markup=reply_markup
            )
            
            return ASKING_WATERMARK
    
    async def handle_watermark_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user's response to watermark question."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data == "watermark_yes":
            # User wants to add watermark, show position options
            keyboard = []
            for pos_id, pos_info in WATERMARK_POSITIONS.items():
                keyboard.append([InlineKeyboardButton(pos_info["name"], callback_data=f"watermark_{pos_id}")])
            
            # Add back button
            keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً موقعیت واترمارک را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_WATERMARK_POSITION
            
        elif query.data == "watermark_no":
            # User doesn't want watermark, show main menu
            keyboard = [
                [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
                [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
                [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_OPTION

    async def handle_text_type_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text content type selection and ask for prompt."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Handle back button
        if query.data == "back_to_main":
            # Go back to main menu
            keyboard = [
                [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
                [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_OPTION
        
        content_type = query.data.replace("text_", "")
        
        # Store the content type
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id]["content_type"] = content_type
        
        await query.edit_message_text(
            f"لطفاً توضیح دهید که محتوای {content_type} برای چه منظوری تولید شود:\n\n"
            "مثال: برای معرفی محصول، تبلیغات، شبکه‌های اجتماعی و غیره"
        )
        
        return WAITING_FOR_TEXT_PROMPT
    
    async def handle_text_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text prompt and generate content."""
        user_id = update.message.from_user.id
        user_prompt = update.message.text
        
        user_data = self.user_data.get(user_id, {})
        image_url = user_data.get("image_url")
        content_type = user_data.get("content_type")
        
        if not image_url or not content_type:
            await update.message.reply_text("❌ خطا: اطلاعات ناقص است. لطفاً دوباره تصویر را ارسال کنید.")
            return ConversationHandler.END
        
        # Show processing message
        processing_msg = await update.message.reply_text("🔄 در حال تولید محتوای متنی... لطفاً صبر کنید.")
        
        try:
            # Create the full prompt
            full_prompt = f"Generate {content_type} content for this product. User request: {user_prompt}"
            
            # Call the API
            result = await self.api_client.generate_text_content(
                image_url=image_url,
                prompt=full_prompt
            )
            
            # Debug: Log the result
            logger.info(f"Text API Result: {result}")
            
            if result and result.get("output"):
                # Send the generated text
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ محتوای {content_type} تولید شد:\n\n{result['output']}"
                )
                success = True
            else:
                logger.warning(f"No valid text result from API: {result}")
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ خطا در تولید محتوای متنی. لطفاً دوباره تلاش کنید."
                )
                success = False
                
        except Exception as e:
            logger.error(f"Error generating text content: {e}")
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ خطا در تولید محتوای متنی. لطفاً دوباره تلاش کنید."
            )
            success = False
        
        # Add a small delay to ensure content is sent first
        import asyncio
        await asyncio.sleep(1)
        
        # Show main menu again for more actions
        keyboard = [
            [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
            [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
            [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=user_id,
            text="لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup
        )
        
        return CHOOSING_OPTION
    
    async def handle_unexpected_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unexpected text messages during conversation."""
        user_id = update.message.from_user.id
        
        await update.message.reply_text(
            "❌ لطفاً از دکمه‌های موجود استفاده کنید یا تصویر جدیدی ارسال کنید."
        )
        
        # Show main menu again
        keyboard = [
            [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
            [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
            [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
            [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup
        )
        
        return CHOOSING_OPTION
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation."""
        user_id = update.message.from_user.id
        
        # Clean up user data
        if user_id in self.user_data:
            del self.user_data[user_id]
        
        await update.message.reply_text("❌ عملیات لغو شد.")
        return ConversationHandler.END
    
    async def handle_watermark_position_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle watermark position selection and add watermark to image."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        # Handle back button
        if query.data == "back_to_main":
            # Go back to main menu
            keyboard = [
                [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
                [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
                [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=reply_markup
            )
            return CHOOSING_OPTION
        
        pos_id = query.data.replace("watermark_", "")
        
        if pos_id in WATERMARK_POSITIONS:
            pos_info = WATERMARK_POSITIONS[pos_id]
            user_data = self.user_data.get(user_id, {})
            
            # Check if we have a generated image URL (from image generation) or original image URL
            image_url = user_data.get("generated_image_url") or user_data.get("image_url")
            
            if not image_url:
                await query.edit_message_text("❌ خطا: تصویر محصول یافت نشد. لطفاً دوباره تصویر را ارسال کنید.")
                return ConversationHandler.END
            
            # Show processing message
            await query.edit_message_text("🔄 در حال افزودن واترمارک... لطفاً صبر کنید.")
            
            try:
                # Add watermark
                watermarked_image_data = self.watermark_processor.add_watermark(
                    image_url=image_url,
                    position=pos_info["value"],
                    opacity=1.0
                )
                
                if watermarked_image_data:
                    # Send the watermarked image
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=watermarked_image_data,
                        caption=f"✅ واترمارک با موفقیت در {pos_info['name']} اضافه شد!"
                    )
                    success = True
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="❌ خطا در افزودن واترمارک. لطفاً دوباره تلاش کنید."
                    )
                    success = False
                    
            except Exception as e:
                logger.error(f"Error adding watermark: {e}")
                await context.bot.send_message(
                    chat_id=user_id,
                    text="❌ خطا در افزودن واترمارک. لطفاً دوباره تلاش کنید."
                )
                success = False
            
            # Add a small delay to ensure image is sent first
            import asyncio
            await asyncio.sleep(1)
            
            # Show main menu again for more actions
            keyboard = [
                [InlineKeyboardButton("تولید تصویر محصول", callback_data="product_image")],
                [InlineKeyboardButton("تولید محتوا متنی", callback_data="text_content")],
                [InlineKeyboardButton("🔒 افزودن واترمارک", callback_data="watermark")],
                [InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=user_id,
                text="لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
                reply_markup=reply_markup
            )
            
            return CHOOSING_OPTION
    
    def run(self):
        """Start the bot."""
        # Create the Application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler("start", self.start),
                MessageHandler(filters.PHOTO, self.handle_image)
            ],
            states={
                CHOOSING_OPTION: [
                    CallbackQueryHandler(self.handle_option_choice),
                    MessageHandler(filters.PHOTO, self.handle_image),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unexpected_text)
                ],
                CHOOSING_SHOT_TYPE: [
                    CallbackQueryHandler(self.handle_shot_type_choice),
                    MessageHandler(filters.PHOTO, self.handle_image),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unexpected_text)
                ],
                CHOOSING_TEXT_TYPE: [
                    CallbackQueryHandler(self.handle_text_type_choice),
                    MessageHandler(filters.PHOTO, self.handle_image),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unexpected_text)
                ],
                WAITING_FOR_TEXT_PROMPT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_prompt),
                    MessageHandler(filters.PHOTO, self.handle_image)
                ],
                CHOOSING_WATERMARK_POSITION: [
                    CallbackQueryHandler(self.handle_watermark_position_choice),
                    MessageHandler(filters.PHOTO, self.handle_image),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unexpected_text)
                ],
                ASKING_WATERMARK: [
                    CallbackQueryHandler(self.handle_watermark_question),
                    MessageHandler(filters.PHOTO, self.handle_image),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unexpected_text)
                ]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)]
        )
        
        application.add_handler(conv_handler)
        
        # Start the bot
        print("🤖 Content Creator Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = ContentCreatorBot()
    bot.run() 