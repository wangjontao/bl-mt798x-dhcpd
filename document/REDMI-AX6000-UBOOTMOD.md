# Redmi AX6000 — OpenWrt ubootmod / FIT test build

This build targets the supplied FastACL 2.5.8 Redmi AX6000 **ubootmod** sysupgrade.itb, SHA256 `e9f4026a1a0c3cc3eb6e3bb0a4e8c0ae50d82c7de5a59aab242eed1b81902f13`.

- Source: wangjontao/bl-mt798x-dhcpd, branch codex/redmi-ax6000-ubootmod-fit.
- U-Boot source: uboot-mtk-20250711; ATF: atf-20240117-bacca82a8 (SP1), normal DDR4 clock settings.
- Raw SPI NAND, **NMBM disabled** in both BL2 and U-Boot.
- FIP at 0x380000, size 0x200000.
- UBI at 0x580000, size 0x7a80000 on the standard 128MiB NAND model.
- FIT configuration config-1; production UBI volume fit. Web recovery retained, default U-Boot IP 192.168.1.1.
- No 110MiB NMBM layout selector. Existing upstream default/multi-layout configuration files remain unchanged; only this branch's configs-fit Redmi AX6000 configuration is adjusted.

## Files

- `JuLiangTK-Redmi-AX6000-ubootmod-SP1-fip.bin`: BL31 + U-Boot FIP container.
- `JuLiangTK-Redmi-AX6000-ubootmod-SP1-bl2.img`: matching raw-NAND BL2.
- `SHA256SUMS`, actual ATF/U-Boot configuration snapshots, source commit and structural validation results.

## Migration boundary

These are bootloader components, **not a LuCI sysupgrade firmware image**. Changing from the existing NMBM 110MiB installation requires a verified flash-backup and partition/UBI migration procedure. Replacing FIP alone does not move the old firmware or recreate its UBI volumes. Do not restore the old NMBM mtdparts environment into this build. Factory/Nvram/Bdata must be preserved.

The compile job checks configuration, image sizes and FIP structure. It cannot verify real flash contents, NAND bad blocks, the existing BL2, or successful hardware boot. No flashing is performed by this workflow.
