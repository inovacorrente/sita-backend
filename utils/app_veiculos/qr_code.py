import logging
import os
from io import BytesIO

import qrcode
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)


def gerar_qr_code(data: str, size: int = 10, border: int = 4) -> Image:
    """
    Gera um QR Code a partir dos dados fornecidos.

    Args:
        data: String com os dados para o QR Code
        size: Tamanho do QR Code (box_size)
        border: Tamanho da borda

    Returns:
        PIL Image object com o QR Code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white")


def criar_banner_com_qr(identificador_veiculo: str,
                        placa: str,
                        usuario_id: int,
                        qr_url: str) -> BytesIO:
    """
    Cria um banner de identificação com QR Code para um veículo.
    Usa a imagem base e adiciona QR Code e informações do veículo.

    Args:
        identificador_veiculo: Identificador único do veículo
        placa: Placa do veículo
        usuario_id: ID do usuário proprietário
        qr_url: URL que será codificada no QR Code

    Returns:
        BytesIO com a imagem do banner gerada
    """
    try:
        # Carregar a imagem base do banner
        banner_path = os.path.join(
            settings.BASE_DIR, 'utils', 'images', 'banner_identificacao.png')
        if not os.path.exists(banner_path):
            raise FileNotFoundError(
                f"Banner base não encontrado em {banner_path}")

        banner = Image.open(banner_path)
        draw = ImageDraw.Draw(banner)

        # Tentar carregar fontes
        try:
            font_tamanho = 55
            font_small = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_tamanho)
        except (OSError, IOError):
            font_small = ImageFont.load_default()

        # === GERAR E POSICIONAR QR CODE ===
        # Gerar QR Code
        qr_image = gerar_qr_code(qr_url, size=3, border=1)

        # Tamanho do QR Code menor, como na imagem ideal
        qr_size = 380  # Tamanho menor para ficar proporcional
        qr_image = qr_image.resize((qr_size, qr_size),
                                   Image.Resampling.LANCZOS)

        # Posicionar QR Code no lado direito, mais centralizado
        qr_margin = 280  # Margem maior da borda direita
        qr_x = banner.width - qr_size - qr_margin

        # Posicionar verticalmente na parte superior-central
        qr_y = 320  # Mais próximo do topo
        banner.paste(qr_image, (qr_x, qr_y))

        # === ADICIONAR INFORMAÇÕES DO VEÍCULO ===
        # Cor do texto (preto)
        text_color = (0, 0, 0)

        # Posicionar texto abaixo do QR Code
        text_area_y = qr_y + qr_size + 8

        # Texto do identificador centralizado abaixo do QR
        id_text = identificador_veiculo
        bbox = draw.textbbox((0, 0), id_text, font=font_small)
        text_width = bbox[2] - bbox[0]
        text_x = qr_x + (qr_size - text_width) // 2

        # Verificar se há espaço suficiente para o texto
        if text_area_y + 15 <= banner.height:
            draw.text((text_x, text_area_y), id_text, fill=text_color,
                      font=font_small)

        # Salvar em BytesIO
        output = BytesIO()
        banner.save(output, format='PNG', quality=95)
        output.seek(0)

        logger.info(
            f"Banner gerado com sucesso para veículo "
            f"{identificador_veiculo} ({placa})")
        return output

    except Exception as e:
        logger.error(
            f"Erro ao gerar banner para veículo "
            f"{identificador_veiculo}: {str(e)}")
        raise
