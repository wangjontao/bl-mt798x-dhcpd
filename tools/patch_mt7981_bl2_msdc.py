#!/usr/bin/env python3
import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_file(path: Path, clock_enable_fix: bool) -> None:
    text = path.read_text()

    text = replace_once(
        text,
        "\tif (!msdc_cmd_is_ready(host))\n"
        "\t\treturn -EIO;\n\n"
        "\tmsdc_fifo_clr(host);\n",
        "\tif (!msdc_cmd_is_ready(host))\n"
        "\t\treturn -EIO;\n\n"
        "\t/* Match U-Boot recovery: do not start a command with stale FIFO data. */\n"
        "\tif (msdc_fifo_tx_bytes(host) || msdc_fifo_rx_bytes(host)) {\n"
        "\t\tERROR(\"MSDC: TX/RX FIFO non-empty before command, resetting\\n\");\n"
        "\t\tmsdc_reset_hw(host);\n"
        "\t}\n\n"
        "\tmsdc_fifo_clr(host);\n",
        "pre-command FIFO recovery",
    )

    text = replace_once(
        text,
        "\tmmio_write_32((uintptr_t)&host->base->msdc_int, CMD_INTS_MASK);\n"
        "\tmmio_write_32((uintptr_t)&host->base->sdc_blk_num, blocks);\n",
        "\t/*\n"
        "\t * Clear stale command AND data interrupt status before issuing the\n"
        "\t * command. U-Boot does this before CMD17/CMD18; clearing DATA_INTS\n"
        "\t * after the command can race with a freshly completed transfer.\n"
        "\t */\n"
        "\tmmio_write_32((uintptr_t)&host->base->msdc_int, CMD_INTS_MASK);\n"
        "\tmmio_write_32((uintptr_t)&host->base->msdc_int, DATA_INTS_MASK);\n"
        "\tmmio_write_32((uintptr_t)&host->base->sdc_blk_num, blocks);\n",
        "interrupt pre-clear",
    )

    text = replace_once(
        text,
        "\tcmd_idx = mmio_read_32((uintptr_t)&host->base->sdc_cmd) & 0x3f;\n"
        "\tcmd_arg = mmio_read_32((uintptr_t)&host->base->sdc_arg);\n\n"
        "\tmmio_write_32((uintptr_t)&host->base->msdc_int, DATA_INTS_MASK);\n\n"
        "\twhile (1) {\n",
        "\tcmd_idx = mmio_read_32((uintptr_t)&host->base->sdc_cmd) & 0x3f;\n"
        "\tcmd_arg = mmio_read_32((uintptr_t)&host->base->sdc_arg);\n\n"
        "\twhile (1) {\n",
        "late data interrupt clear",
    )

    text = replace_once(
        text,
        "\t}\n\n"
        "\treturn ret;\n"
        "}\n\n"
        "static int mtk_mmc_write(int lba, uintptr_t buf, size_t size)\n",
        "\t}\n\n"
        "\t/* Match U-Boot: recover the controller and FIFO after data errors. */\n"
        "\tif (ret) {\n"
        "\t\tERROR(\"MSDC: read failed (%d), resetting controller\\n\", ret);\n"
        "\t\tmsdc_reset_hw(host);\n"
        "\t\tmsdc_fifo_clr(host);\n"
        "\t}\n\n"
        "\treturn ret;\n"
        "}\n\n"
        "static int mtk_mmc_write(int lba, uintptr_t buf, size_t size)\n",
        "read error recovery",
    )

    if clock_enable_fix:
        text = replace_once(
            text,
            "\treadl_poll_timeout(&host->base->msdc_cfg, reg,\n"
            "\t\t\t   reg & MSDC_CFG_CKSTB, 1000000);\n\n"
            "\thost->sclk = sclk;\n",
            "\treadl_poll_timeout(&host->base->msdc_cfg, reg,\n"
            "\t\t\t   reg & MSDC_CFG_CKSTB, 1000000);\n\n"
            "\t/* Keep the bus clock enabled after changing the divider, as U-Boot does. */\n"
            "\tmmio_setbits_32((uintptr_t)&host->base->msdc_cfg, MSDC_CFG_CKPDN);\n\n"
            "\thost->sclk = sclk;\n",
            "clock enable after divider change",
        )

    path.write_text(text)
    print(f"patched {path} (clock_enable_fix={clock_enable_fix})")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", default="atf-20250711")
    ap.add_argument("--clock-enable-fix", action="store_true")
    args = ap.parse_args()

    path = Path(args.tree) / "plat/mediatek/apsoc_common/drivers/mmc/mtk-sd.c"
    if not path.is_file():
        raise SystemExit(f"source file not found: {path}")
    patch_file(path, args.clock_enable_fix)


if __name__ == "__main__":
    main()
