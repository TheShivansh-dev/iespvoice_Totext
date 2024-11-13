import os
import pandas as pd
import datetime
import time
import subprocess
import speech_recognition as sr
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Bot configuration
TOKEN = '7007935023:AAENkGaklw6LMJA_sfhVZhnoAgIjW4lDTBc'
BOT_USERNAME = '@Grovieee_bot'
TARGET_USER_ID = 1067127529




# Send the paragraph when /readandrecord command is used

# Transcribe voice message and include sender's details
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print('Enter here')
    start_time = time.time()  # Record start time

    # Get sender information
    user = update.message.from_user
    username = user.username or "Unknown"
    user_id = user.id

    # Download the voice message
    file = await update.message.voice.get_file()
    file_path = "voice_message.ogg"
    await file.download_to_drive(file_path)
    print(f"Downloaded file: {file_path}")  # Check the file path

    # Convert OGG to WAV using ffmpeg
    wav_path = "voice_message.wav"
    try:
        # Specify the full path to ffmpeg if it's not in PATH
        ffmpeg_path = "/app/.heroku/bin/ffmpeg"



        # Print the ffmpeg command being run for debugging
        print(f"Running ffmpeg: {ffmpeg_path} -i {file_path} {wav_path}")

        conversion_start_time = time.time()  # Record time for conversion
        subprocess.run([ffmpeg_path, '-i', file_path, wav_path])  # Run ffmpeg with the specified path
        conversion_time = time.time() - conversion_start_time
        print(f"FFmpeg conversion took {conversion_time:.2f} seconds.")

        # Transcribe the audio
        transcription_start_time = time.time()  # Record time for transcription
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as audio_file:
            audio_data = recognizer.record(audio_file)
            text = recognizer.recognize_google(audio_data)

        transcription_time = time.time() - transcription_start_time
        print(f"Transcription took {transcription_time:.2f} seconds.")
        print(f"Transcription: {text}")  # Print transcription in the console

        # Add user details to the transcription
        transcription_with_details = (
            f"Transcription: {text}\n\n"
            f"Recorded by username: @{username} | ID: {user_id}"
        )

        # Respond to the user with transcription and sender details
        #await update.message.reply_text(transcription_with_details)
        await context.bot.send_message(chat_id=TARGET_USER_ID, text=transcription_with_details)

    except Exception as e:
        print("Error transcribing audio:", e)
        transcription_with_details_error = (
            f"Sorry, I couldn’t transcribe the audio.\n\n"
            f"For username: @{username} | ID: {user_id}"
        )
        await context.bot.send_message(chat_id=TARGET_USER_ID, text=transcription_with_details_error)
    
    # Delete audio files after processing
    try:
        os.remove(file_path)
        os.remove(wav_path)
        print("Temporary files deleted successfully.")
    except Exception as e:
        print(f"Error deleting files: {e}")

    total_time = time.time() - start_time
    print(f"Total time for processing: {total_time:.2f} seconds.")

# Main function
def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))  # Removed ALLOWED_GROUP_ID to work for all groups
    
    # Run the bot
    application.run_polling()

if __name__ == '__main__':
    main()
