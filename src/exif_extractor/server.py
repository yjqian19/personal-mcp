"""
EXIF Information Extraction MCP Server
Supports JPG and PNG image EXIF data extraction
"""

import base64
import io
from typing import Dict, Any
from urllib.parse import urlparse

import piexif
import requests
from mcp.server.fastmcp import Context, FastMCP
from PIL import Image
from pydantic import BaseModel, Field

from smithery.decorators import smithery


class ExifConfig(BaseModel):
    """EXIF extractor configuration"""
    timeout: int = Field(30, description="Request timeout in seconds")
    max_file_size: int = Field(50 * 1024 * 1024, description="Maximum file size in bytes, default 50MB")
    include_technical: bool = Field(True, description="Include technical parameters (aperture, shutter, etc.)")
    include_location: bool = Field(False, description="Include location information (GPS)")


@smithery.server(config_schema=ExifConfig)
def create_server():
    """Create EXIF extractor MCP server"""

    server = FastMCP("EXIF Extractor")

    def _get_image_from_url(url: str, config: ExifConfig) -> Image.Image:
        """Get image from URL"""
        try:
            response = requests.get(url, timeout=config.timeout)
            response.raise_for_status()

            if len(response.content) > config.max_file_size:
                raise ValueError(f"File too large, exceeds {config.max_file_size // (1024*1024)}MB limit")

            return Image.open(io.BytesIO(response.content))

        except requests.RequestException as e:
            raise ValueError(f"Failed to download image: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

    def _get_image_from_base64(base64_data: str) -> Image.Image:
        """Get image from Base64 data"""
        try:
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            image_data = base64.b64decode(base64_data)
            return Image.open(io.BytesIO(image_data))
        except Exception as e:
            raise ValueError(f"Failed to parse Base64 image: {str(e)}")

    def _extract_exif_from_pil(image: Image.Image) -> Dict[str, Any]:
        """Extract EXIF data from PIL Image object"""
        exif_data = {}

        if hasattr(image, '_getexif') and image._getexif() is not None:
            exif_dict = image._getexif()
            exif_data = piexif.load(str(exif_dict))
        elif 'exif' in image.info:
            exif_data = piexif.load(image.info['exif'])

        return exif_data


    def _format_exif_info(exif_data: Dict[str, Any], config: ExifConfig, image: Image.Image = None) -> str:
        """Format EXIF information into readable text"""
        if not exif_data:
            return "❌ No EXIF information found"

        result = "📸 Image EXIF Information:\n"
        result += "=" * 50 + "\n\n"

        # Basic information
        if '0th' in exif_data:
            basic_info = exif_data['0th']

            # Camera information
            if piexif.ImageIFD.Make in basic_info:
                result += f"📷 Camera Make: {basic_info[piexif.ImageIFD.Make].decode('utf-8')}\n"

            if piexif.ImageIFD.Model in basic_info:
                result += f"📱 Camera Model: {basic_info[piexif.ImageIFD.Model].decode('utf-8')}\n"

            # Date and time
            if piexif.ImageIFD.DateTime in basic_info:
                result += f"📅 Date Taken: {basic_info[piexif.ImageIFD.DateTime].decode('utf-8')}\n"

            # Software
            if piexif.ImageIFD.Software in basic_info:
                result += f"💻 Software: {basic_info[piexif.ImageIFD.Software].decode('utf-8')}\n"

        # Technical parameters
        if config.include_technical and 'Exif' in exif_data:
            exif_info = exif_data['Exif']
            result += "\n🔧 Technical Parameters:\n"
            result += "-" * 30 + "\n"

            # Aperture
            if piexif.ExifIFD.FNumber in exif_info:
                f_number = exif_info[piexif.ExifIFD.FNumber]
                aperture = f_number[0] / f_number[1] if isinstance(f_number, tuple) else f_number
                result += f"🔍 Aperture: f/{aperture:.1f}\n"

            # Shutter speed
            if piexif.ExifIFD.ExposureTime in exif_info:
                exposure = exif_info[piexif.ExifIFD.ExposureTime]
                if isinstance(exposure, tuple):
                    shutter = f"{exposure[0]}/{exposure[1]}s"
                else:
                    shutter = f"{exposure}s"
                result += f"⏱️ Shutter Speed: {shutter}\n"

            # ISO
            if piexif.ExifIFD.ISOSpeedRatings in exif_info:
                iso = exif_info[piexif.ExifIFD.ISOSpeedRatings]
                result += f"📊 ISO: {iso}\n"

            # Focal length
            if piexif.ExifIFD.FocalLength in exif_info:
                focal = exif_info[piexif.ExifIFD.FocalLength]
                if isinstance(focal, tuple):
                    focal_length = f"{focal[0]}/{focal[1]}mm"
                else:
                    focal_length = f"{focal}mm"
                result += f"🔭 Focal Length: {focal_length}\n"

            # Flash
            if piexif.ExifIFD.Flash in exif_info:
                flash = exif_info[piexif.ExifIFD.Flash]
                flash_text = "On" if flash & 0x01 else "Off"
                result += f"💡 Flash: {flash_text}\n"

            # White balance
            if piexif.ExifIFD.WhiteBalance in exif_info:
                wb = exif_info[piexif.ExifIFD.WhiteBalance]
                wb_text = "Auto" if wb == 0 else "Manual"
                result += f"🎨 White Balance: {wb_text}\n"

        # Image information
        if image:
            result += "\n📐 Image Information:\n"
            result += "-" * 30 + "\n"
            result += f"🖼️ Dimensions: {image.size[0]} × {image.size[1]} pixels\n"
            result += f"🎨 Color Mode: {image.mode}\n"
            result += f"📁 Format: {image.format}\n"

        return result

    @server.tool()
    def extract_exif(image_input: str, ctx: Context) -> str:
        """Extract EXIF information from image URL or Base64 data"""
        config = ctx.session_config

        try:
            # Check if input is URL or Base64
            if image_input.startswith(('http://', 'https://')):
                # URL input
                parsed_url = urlparse(image_input)
                if not parsed_url.scheme or not parsed_url.netloc:
                    return "❌ Invalid image URL"

                # Process regular image (JPG/PNG)
                image = _get_image_from_url(image_input, config)
                exif_data = _extract_exif_from_pil(image)
            else:
                # Base64 input
                image = _get_image_from_base64(image_input)

                # Check file size
                if len(base64.b64decode(image_input.split(',')[1] if ',' in image_input else image_input)) > config.max_file_size:
                    return f"❌ File too large, exceeds {config.max_file_size // (1024*1024)}MB limit"

                exif_data = _extract_exif_from_pil(image)

            # Format output
            return _format_exif_info(exif_data, config, image)

        except ValueError as e:
            return f"❌ Error: {str(e)}"
        except Exception as e:
            return f"❌ Processing failed: {str(e)}"

    @server.resource("exif://supported-formats")
    def supported_formats() -> str:
        """Supported image formats information"""
        return """
📸 Supported Image Formats:

🖼️ Standard Formats:
• JPEG/JPG - Most common digital photo format
• PNG - Lossless compression format, often used for screenshots

📊 Extracted EXIF Information:
• Camera make and model
• Date and time taken
• Technical parameters (aperture, shutter, ISO, focal length)
• Flash and white balance settings
• Image dimensions and format information

⚠️ Notes:
• Some images may not have EXIF information
• File size limit is 50MB
        """

    return server
