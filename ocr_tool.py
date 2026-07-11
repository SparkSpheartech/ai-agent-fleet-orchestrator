from PIL import Image
import pytesseract
import argparse

def image_to_text(image_path, lang=\'eng\'):
    """
    Converts text from an image file to a string using Tesseract OCR.

    Args:
        image_path (str): The path to the input image file.
        lang (str): The language of the text in the image (e.g., \'eng\' for English).

    Returns:
        str: The extracted text from the image.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang)
        return text
    except pytesseract.TesseractNotFoundError:
        return "Tesseract is not installed or not in your PATH. Please install it."
    except FileNotFoundError:
        return f"Error: Image file not found at {image_path}"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == \'__main__\':
    parser = argparse.ArgumentParser(description=\'Convert image to text using Tesseract OCR.\')
    parser.add_argument(\'image_path\', type=str, help=\'Path to the input image file.\')
    parser.add_argument(\'--lang\', type=str, default=\'eng\', help=\'Language of the text in the image (default: eng).\')

    args = parser.parse_args()

    extracted_text = image_to_text(args.image_path, args.lang)
    print(extracted_text)
