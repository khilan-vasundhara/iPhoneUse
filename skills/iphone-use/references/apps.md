# Finding the Real App Bundle ID

A bundle ID that is already known and verified can be launched directly; do not re-check the installed list on every launch. To look up common apps, first use `pua_apps(source="catalog")` to search the local catalog offline; for an unknown app, or when you need to tell apart the version the user actually has installed, use source=auto, which checks the selected iPhone's installed apps first, then the local catalog, and only queries Apple if there is still no candidate. Do not spell a bundle ID from a brand name, and do not try several guessed values in a row.

```json
{"query":"China Merchants Bank","source":"auto"}
```

This example should return `com.cmbchina.MPBBank`. After checking the name, publisher, and candidate source, pass the bundle_id to `pua_launch_app`. A normal launch continues optimistically; when the next step needs information about an unknown page, set observe on that launch to also see the actual foreground and the target page, without adding a default launch verification. The China Merchants Bank main app and the Zhangshang Shenghuo (CMB Life) credit card app are two different apps.

- `source=auto`: first reads the selected device's installed list (cached locally for 300 seconds) and merges the local catalog. Exact names/aliases take priority; when an exact match exists, substring candidates are not mixed in. Apple is only called when there is no local candidate.
- `source=installed`: queries only the selected iPhone; when no device is selected or reading fails, it returns actionable diagnostics. English brand aliases can be mapped to bundle IDs in the installed list through the local catalog.
- `source=catalog`: offline lookup of the 36 apps in this file and `apps.json` that were verified through Apple queries. It does not query the iPhone or the network at all.
- `source=apple`: queries Apple's public API for the specified App Store country/region, defaulting to `country=cn`; you can specify `hk`, `us`, and so on. It returns store candidates, which does not mean they are installed on the user's phone.

`installed_verified=true` means the selected device's installed list confirmed the candidate; `installation_checked` indicates whether this query successfully obtained the installed list (cached for up to five minutes); false cannot independently be read as not installed. `verified_at` on a candidate is the source verification time. The query returns only matching apps and does not send back the whole device inventory. The device installed list and cache are kept in a private state directory outside the repository with permission 600; device information or the installed list is never sent to Apple.

## Official Apple API

The [Apple iTunes Search API documentation](https://performance-partners.apple.com/search-api) describes `software`, the country/region parameter, JSON, caching, and a guideline limit of about 20 queries per minute. This public endpoint queries App Store app metadata and needs no Apple ID, password, or API key from the user:

```text
https://itunes.apple.com/search?term=China%20Merchants%20Bank&country=cn&media=software&entity=software&limit=10
https://itunes.apple.com/lookup?id=392899425&country=cn&entity=software
```

Search by name first and check the actual publisher and product, then refresh with a Lookup by the stable `trackId`. The official documentation states that ID lookups mismatch less; do not automatically pick the first name-search result. `pua_apps` uses URL encoding, a 5-second network timeout, a response size limit, Apple HTTPS domain/path and redirect restrictions, a 15-minute cache, and at most 18 new requests per minute, to avoid long blocking or repeatedly hitting the rate limit. The refresh script does batch Lookups of the reviewed IDs by region.

```sh
python3 scripts/update_app_catalog.py --search "App name" --country cn
python3 scripts/update_app_catalog.py --refresh
```

Search only prints candidates and does not add them to the catalog automatically. A maintainer adds a record after checking the App Store page, the publisher, and the specific product; refresh only updates store metadata of existing reviewed records, and stops and keeps the original catalog if an ID is missing or a bundle ID changes.

## Scope and failure handling

Apple store search has same-name, region, and delisting limits, and enterprise-internal, development, or unlisted apps may not exist. The [App Store Connect bundleIds endpoint](https://developer.apple.com/documentation/appstoreconnectapi/get-v1-bundleids) can only list IDs registered by the developer's own team and cannot be used as a catalog of all third-party apps. The installed device list is more direct evidence for confirming what the user actually has.

In this hands-on test, searching CN for `Futu NiuNiu` found no target app, and only a query on HK retrieved `cn.futu.FutuTraderPhone`. For an empty result, first check `source=installed`, or query the user's actual store region; do not interpret not finding it in a region search as not installed. Feishu vs. the international Lark, WeChat vs. WeCom, and regular vs. lite/development editions should also each be checked separately.

If the MCP query itself is unavailable, you can use the fixed Xcode command to read the local installed list directly (`--include-all-apps` must be kept: devicectl lists only development apps by default), filter the target name/bundle ID locally, and then launch. The observation needed for the next step can also be used to judge the launch state along the way. Write the file to a private directory outside the repository, and do not save the full installed inventory in the project:

```sh
xcrun devicectl device info apps --device "<selected device UDID>" --include-all-apps --json-output "<private directory>/apps.json" --timeout 8
```

## Verified catalog

The actual Apple API URL, store name, publisher, country/region, and UTC verification time of each record are in [apps.json](apps.json). Below are only the brand, bundle ID, and queried region; a store record does not prove the device installation state.

| App | bundle ID | Verified store |
| --- | --- | --- |
| WeChat | `com.tencent.xin` | [CN](https://apps.apple.com/cn/app/id414478124) |
| Alipay | `com.alipay.iphoneclient` | [CN](https://apps.apple.com/cn/app/id333206289) |
| Taobao | `com.taobao.taobao4iphone` | [CN](https://apps.apple.com/cn/app/id387682726) |
| JD | `com.360buy.jdmobile` | [CN](https://apps.apple.com/cn/app/id414245413) |
| Pinduoduo | `com.xunmeng.pinduoduo` | [CN](https://apps.apple.com/cn/app/id1044283059) |
| Xiaohongshu (RED) | `com.xingin.discover` | [CN](https://apps.apple.com/cn/app/id741292507) |
| Douyin | `com.ss.iphone.ugc.Aweme` | [CN](https://apps.apple.com/cn/app/id1142110895) |
| Kuaishou | `com.jiangjia.gif` | [CN](https://apps.apple.com/cn/app/id440948110) |
| Bilibili | `tv.danmaku.bilianime` | [CN](https://apps.apple.com/cn/app/id736536022) |
| Weibo | `com.sina.weibo` | [CN](https://apps.apple.com/cn/app/id350962117) |
| QQ | `com.tencent.mqq` | [CN](https://apps.apple.com/cn/app/id444934666) |
| QQ Music | `com.tencent.QQMusic` | [CN](https://apps.apple.com/cn/app/id414603431) |
| NetEase Cloud Music | `com.netease.cloudmusic` | [CN](https://apps.apple.com/cn/app/id590338362) |
| Baidu Maps | `com.baidu.map` | [CN](https://apps.apple.com/cn/app/id452186370) |
| Amap (AutoNavi) | `com.autonavi.amap` | [CN](https://apps.apple.com/cn/app/id461703208) |
| DiDi | `com.xiaojukeji.didi` | [CN](https://apps.apple.com/cn/app/id554499054) |
| Meituan | `com.meituan.imeituan` | [CN](https://apps.apple.com/cn/app/id423084029) |
| Ele.me | `me.ele.ios.eleme` | [CN](https://apps.apple.com/cn/app/id507161324) |
| Ctrip | `ctrip.com` | [CN](https://apps.apple.com/cn/app/id379395415) |
| Fliggy | `com.taobao.travel` | [CN](https://apps.apple.com/cn/app/id453691481) |
| China Railway 12306 | `cn.12306.rails12306` | [CN](https://apps.apple.com/cn/app/id564818797) |
| Baidu Netdisk | `com.baidu.netdisk` | [CN](https://apps.apple.com/cn/app/id547166701) |
| Tencent Meeting | `com.tencent.meeting` | [CN](https://apps.apple.com/cn/app/id1484048379) |
| DingTalk | `com.laiwang.DingTalk` | [CN](https://apps.apple.com/cn/app/id930368978) |
| Feishu | `com.bytedance.ee.lark` | [CN](https://apps.apple.com/cn/app/id1401729613) |
| WeCom | `com.tencent.ww` | [CN](https://apps.apple.com/cn/app/id1087897068) |
| China Merchants Bank | `com.cmbchina.MPBBank` | [CN](https://apps.apple.com/cn/app/id392899425) |
| CMB Life (Zhangshang Shenghuo) | `com.cmbchina.cmblife` | [CN](https://apps.apple.com/cn/app/id398453262) |
| ICBC | `com.icbc.iphoneclient` | [CN](https://apps.apple.com/cn/app/id423514795) |
| China Construction Bank | `com.ccb.ccbDemo` | [CN](https://apps.apple.com/cn/app/id391965015) |
| Agricultural Bank of China | `com.bankabc.iphonerelease` | [CN](https://apps.apple.com/cn/app/id515651240) |
| Bank of China | `com.boc.BOCMBCI` | [CN](https://apps.apple.com/cn/app/id399608199) |
| Xueqiu (Snowball) | `com.xueqiu` | [CN](https://apps.apple.com/cn/app/id492180369) |
| Tonghuashun | `cn.com.10jqka.IHexin` | [CN](https://apps.apple.com/cn/app/id303191318) |
| Eastmoney | `com.eastmoney.iphone` | [CN](https://apps.apple.com/cn/app/id423525686) |
| Futu NiuNiu | `cn.futu.FutuTraderPhone` | [HK](https://apps.apple.com/hk/app/id592031984) |
