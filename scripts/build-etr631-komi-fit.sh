#!/bin/bash
set -euo pipefail
cfg=uboot-mtk-20250711/configs-fit/mt7981_konka_komi-a31_defconfig
# Fixed 128MB SPI-NAND layout matching the supplied 6.6.133 FIT firmware.
grep -q '1024k(bl2),512k(u-boot-env),2048k(factory),2048k(fip),-(ubi)' "$cfg"
cat >> "$cfg" <<'CONFIG'
CONFIG_MTK_DHCPD=y
CONFIG_MTK_DHCPD_USE_CONFIG_IP=y
CONFIG_WEBUI_FAILSAFE_UI_BOOTSTRAP=y
CONFIG_WEBUI_FAILSAFE_I18N=y
CONFIG_WEBUI_FAILSAFE_ADVANCED=y
CONFIG_WEBUI_FAILSAFE_BACKUP=y
CONFIG_WEBUI_FAILSAFE_UBI=y
# CONFIG_ENABLE_NAND_NMBM is not set
CONFIG
BOARD=konka_komi-a31 SOC=mt7981 VERSION=2025 VARIANT=ubootmod MULTI_LAYOUT=0 FIXED_MTDPARTS=0 COPY_BL2=1 UBIMNG=1 SILENT=Y bash build.sh
c=uboot-mtk-20250711/.config
for setting in CONFIG_MTK_BOOTMENU_UBI CONFIG_FIT CONFIG_MTK_DHCPD CONFIG_ENV_IS_IN_UBI CONFIG_MTK_WEB_FAILSAFE; do grep -qx "$setting=y" "$c"; done
! grep -qx 'CONFIG_ENABLE_NAND_NMBM=y' "$c"
fip=$(find output -maxdepth 1 -name 'fip-*.bin' -print -quit)
bl2=$(find output -maxdepth 1 -name 'bl2-*.img' -print -quit)
test -n "$fip" && test -n "$bl2"
test "$(stat -c%s "$fip")" -le 2097152
test "$(stat -c%s "$bl2")" -le 1048576
cp "$fip" output/etr631-komi-a31-ubootmod-bl31-uboot.fip
cp "$bl2" output/etr631-komi-a31-ubootmod-preloader.bin
cp "$c" output/u-boot.config
cp atf-20250711/build/.config output/atf.config
cp uboot-mtk-20250711/u-boot.bin output/u-boot.bin
cat > output/README.txt <<'DOC'
ETR631 using KOMI A31 board profile, MT7981, 256MB RAM, 128MB SPI-NAND, Ubootmod FIT layout.
Built for supplied firmware SHA256 796d20195c563b378a92b033be3143c766460fee6644860391ff5b759c5815e2.
BL2: offset 0x0, maximum 0x100000.
Environment reserved: 0x100000 / 0x80000.
factory RF calibration: 0x180000 / 0x200000. Preserve this partition.
FIP: offset 0x380000, maximum 0x200000.
UBI: offset 0x580000 / 0x7a80000. FIT volume boot, no NMBM.
Recovery web address: http://192.168.1.1, DHCP enabled.
FIP contains BL31 and U-Boot. u-boot.bin is NOT a directly flashable FIP.
Preloader is a separate BL2 image. Do not flash it without confirming hardware and current layout.
Build/config/size checks only; no physical-device boot validation.
DOC
(cd output && sha256sum *.bin *.img *.fip > SHA256SUMS)
git rev-parse HEAD > output/SOURCE_COMMIT.txt
