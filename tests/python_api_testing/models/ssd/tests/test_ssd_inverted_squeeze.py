from pathlib import Path
import sys

f = f"{Path(__file__).parent}"
sys.path.append(f"{f}")
sys.path.append(f"{f}/../../../..")

import torch
import pytest
from loguru import logger
from torchvision.models import mobilenet_v3_large as pretrained
from torchvision.models import MobileNet_V3_Large_Weights

import tt_lib
from python_api_testing.models.utility_functions_new import (
    torch_to_tt_tensor_rm,
    tt_to_torch_tensor,
    comp_allclose,
    comp_pcc,
)
from python_api_testing.models.ssd.tt.ssd_mobilenetv3_inverted_squeeze import (
    TtMobileNetV3InvertedSqueeze,
)


@pytest.mark.parametrize(
    "pcc",
    ((0.99),),
)
def test_ssd_inverted_squeeze_inference(pcc, reset_seeds):
    device = tt_lib.device.CreateDevice(tt_lib.device.Arch.GRAYSKULL, 0)
    tt_lib.device.InitializeDevice(device)
    tt_lib.device.SetDefaultDevice(device)
    host = tt_lib.device.GetHost()

    model = pretrained(weights=MobileNet_V3_Large_Weights.IMAGENET1K_V1)

    # torch invertedsqueeze
    torch_model = model.features[4]

    # Tt ssd_invertedsqueeze
    config = {"in_channels": 24}
    tt_model = TtMobileNetV3InvertedSqueeze(
        config,
        in_channels=config["in_channels"],
        expanded_channels=72,
        out_channels=40,
        kernel_size=5,
        stride=2,
        padding=2,
        state_dict=model.state_dict(),
        base_address=f"features.4",
        device=device,
        host=host,
    )

    # Run torch model
    input_tensor = torch.randn(1, 24, 56, 56)
    torch_output = torch_model(input_tensor)

    # Run tt model
    tt_inverted_squeeze_input = torch_to_tt_tensor_rm(input_tensor, device)
    tt_output = tt_model(tt_inverted_squeeze_input)

    # Compare outputs
    tt_output_torch = tt_to_torch_tensor(tt_output, host)

    does_pass, pcc_message = comp_pcc(torch_output, tt_output_torch, pcc)

    logger.info(comp_allclose(torch_output, tt_output_torch))
    logger.info(pcc_message)

    tt_lib.device.CloseDevice(device)

    if does_pass:
        logger.info("SSDInvertedSqueeze Passed!")

    assert does_pass, "SSDInvertedSqueeze Failed!"
