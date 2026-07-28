#!/usr/bin/env python3
"""
Safe patch applier for shirokhorshid-android.
Run this from inside the shirokhorshid-android repo root:

    python3 apply_patch.py

It will only modify a file if the EXACT old text is found (once).
If not found, it prints an error and leaves the file untouched.
"""

import sys

def apply_patch(filepath, old, new, label):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    count = content.count(old)
    if count == 0:
        print(f"[FAILED] {label}: exact text not found in {filepath}")
        print("         The file may differ from what was expected. No changes made to this file.")
        return False
    if count > 1:
        print(f"[FAILED] {label}: text found {count} times (expected exactly 1) in {filepath}")
        print("         Refusing to guess which one. No changes made to this file.")
        return False

    new_content = content.replace(old, new, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[OK] {label}: patched {filepath}")
    return True


# ---------------------------------------------------------------------------
# Patch 1: TunnelManager.java
# ---------------------------------------------------------------------------
TUNNEL_MANAGER_PATH = "app/src/main/java/com/psiphon3/psiphonlibrary/TunnelManager.java"

TUNNEL_MANAGER_OLD = '''                else if (message.contains("cdn fronting scan found")) {
                    java.util.regex.Pattern pattern = java.util.regex.Pattern.compile(
                            "\\\\(ip: ([^,]+), sni: ([^)]+)\\\\)");
                    java.util.regex.Matcher matcher = pattern.matcher(message);
                    if (matcher.find()) {
                        String ipAddress = unescapeRedactionSafeIPAddress(matcher.group(1));
                        String sniServerName = matcher.group(2);
                        if ("none".equals(sniServerName)) {
                            sniServerName = getContext().getString(R.string.cdn_fronting_scan_no_sni);
                        }
                        MyLog.i(R.string.cdn_fronting_scan_found_with_route, MyLog.Sensitivity.SENSITIVE_FORMAT_ARGS,
                                ipAddress, sniServerName);
                        return;
                    }
                    MyLog.i(R.string.cdn_fronting_scan_found, MyLog.Sensitivity.NOT_SENSITIVE);
                    return;
                }'''

TUNNEL_MANAGER_NEW = '''                else if (message.contains("cdn fronting scan found")) {
                    java.util.regex.Pattern pattern = java.util.regex.Pattern.compile(
                            "\\\\(ip: ([^,]+), sni: ([^)]+)\\\\)");
                    java.util.regex.Matcher matcher = pattern.matcher(message);
                    if (matcher.find()) {
                        String ipAddress = unescapeRedactionSafeIPAddress(matcher.group(1));
                        String rawSni = matcher.group(2);
                        String sniToStore = "none".equals(rawSni) ? "" : rawSni;

                        // Persist the last successfully found bridge so the user can
                        // reuse it later without re-scanning.
                        AppPreferences lastBridgePrefs = new AppPreferences(getContext());
                        lastBridgePrefs.put("cdnFrontingLastFoundIp", ipAddress);
                        lastBridgePrefs.put("cdnFrontingLastFoundSni", sniToStore);

                        String sniServerName = rawSni;
                        if ("none".equals(sniServerName)) {
                            sniServerName = getContext().getString(R.string.cdn_fronting_scan_no_sni);
                        }
                        MyLog.i(R.string.cdn_fronting_scan_found_with_route, MyLog.Sensitivity.SENSITIVE_FORMAT_ARGS,
                                ipAddress, sniServerName);
                        return;
                    }
                    MyLog.i(R.string.cdn_fronting_scan_found, MyLog.Sensitivity.NOT_SENSITIVE);
                    return;
                }'''

# ---------------------------------------------------------------------------
# Patch 2: more_options_preferences.xml
# ---------------------------------------------------------------------------
XML_PATH = "app/src/main/res/xml/more_options_preferences.xml"

XML_OLD = '''        <EditTextPreference
            android:icon="@drawable/ic_tls_sni"
            android:key="@string/cdnFrontingCustomSniPreference"
            android:inputType="textMultiLine|textNoSuggestions"
            android:summary="@string/cdnFrontingCustomSniPreferenceSummary"
            android:title="@string/cdnFrontingCustomSniPreferenceTitle" />
    </PreferenceCategory>'''

XML_NEW = '''        <EditTextPreference
            android:icon="@drawable/ic_tls_sni"
            android:key="@string/cdnFrontingCustomSniPreference"
            android:inputType="textMultiLine|textNoSuggestions"
            android:summary="@string/cdnFrontingCustomSniPreferenceSummary"
            android:title="@string/cdnFrontingCustomSniPreferenceTitle" />
        <Preference
            android:key="useLastFoundCdnBridge"
            android:title="\u0627\u0633\u062a\u0641\u0627\u062f\u0647 \u0627\u0632 \u0622\u062e\u0631\u06cc\u0646 \u067e\u0644 \u067e\u06cc\u062f\u0627\u200c\u0634\u062f\u0647"
            android:summary="\u0622\u062e\u0631\u06cc\u0646 IP \u0648 SNI \u06a9\u0647 \u0627\u0633\u06a9\u0646\u0631 \u067e\u06cc\u062f\u0627 \u06a9\u0631\u062f\u0647 \u0631\u0627 \u062f\u0631 \u0641\u06cc\u0644\u062f\u0647\u0627\u06cc \u0628\u0627\u0644\u0627 \u0642\u0631\u0627\u0631 \u0645\u06cc\u200c\u062f\u0647\u062f" />
    </PreferenceCategory>'''

# ---------------------------------------------------------------------------
# Patch 3: MoreOptionsPreferenceActivity.java
# ---------------------------------------------------------------------------
ACTIVITY_PATH = "app/src/main/java/com/psiphon3/psiphonlibrary/MoreOptionsPreferenceActivity.java"

ACTIVITY_IMPORT_OLD = '''import com.psiphon3.MainActivityViewModel;
import com.psiphon3.R;

import java.util.Locale;'''

ACTIVITY_IMPORT_NEW = '''import com.psiphon3.MainActivityViewModel;
import com.psiphon3.R;

import net.grandcentrix.tray.AppPreferences;

import java.util.Locale;'''

ACTIVITY_BODY_OLD = '''                mCdnFrontingCustomSni.setOnPreferenceChangeListener((preference, newValue) -> {
                    updateCdnFrontingCustomSniSummary(
                            (EditTextPreference) preference, (String) newValue);
                    return true;
                });
            }'''

ACTIVITY_BODY_NEW = '''                mCdnFrontingCustomSni.setOnPreferenceChangeListener((preference, newValue) -> {
                    updateCdnFrontingCustomSniSummary(
                            (EditTextPreference) preference, (String) newValue);
                    return true;
                });
            }

            Preference useLastFoundBridge = preferences.findPreference("useLastFoundCdnBridge");
            if (useLastFoundBridge != null) {
                useLastFoundBridge.setOnPreferenceClickListener(preference -> {
                    AppPreferences appPrefs = new AppPreferences(getContext());
                    String lastIp = appPrefs.getString("cdnFrontingLastFoundIp", "");
                    String lastSni = appPrefs.getString("cdnFrontingLastFoundSni", "");
                    if (TextUtils.isEmpty(lastIp)) {
                        Toast.makeText(getContext(), "\u0647\u0646\u0648\u0632 \u0647\u06cc\u0686 \u067e\u0644\u06cc \u067e\u06cc\u062f\u0627 \u0646\u0634\u062f\u0647", Toast.LENGTH_SHORT).show();
                        return true;
                    }
                    if (mCdnFrontingCustomIpList != null) {
                        mCdnFrontingCustomIpList.setText(lastIp);
                        updateCdnFrontingCustomIpSummary(mCdnFrontingCustomIpList, lastIp);
                    }
                    if (mCdnFrontingCustomSni != null) {
                        mCdnFrontingCustomSni.setText(lastSni);
                        updateCdnFrontingCustomSniSummary(mCdnFrontingCustomSni, lastSni);
                    }
                    Toast.makeText(getContext(), "\u067e\u0644 \u0642\u0628\u0644\u06cc \u0627\u0639\u0645\u0627\u0644 \u0634\u062f", Toast.LENGTH_SHORT).show();
                    return true;
                });
            }'''


def main():
    results = []
    results.append(apply_patch(TUNNEL_MANAGER_PATH, TUNNEL_MANAGER_OLD, TUNNEL_MANAGER_NEW, "TunnelManager.java (scan-found block)"))
    results.append(apply_patch(XML_PATH, XML_OLD, XML_NEW, "more_options_preferences.xml (new Preference entry)"))
    results.append(apply_patch(ACTIVITY_PATH, ACTIVITY_IMPORT_OLD, ACTIVITY_IMPORT_NEW, "MoreOptionsPreferenceActivity.java (import)"))
    results.append(apply_patch(ACTIVITY_PATH, ACTIVITY_BODY_OLD, ACTIVITY_BODY_NEW, "MoreOptionsPreferenceActivity.java (click listener)"))

    print()
    if all(results):
        print("All patches applied successfully.")
    else:
        print("Some patches FAILED — see messages above. Fix manually or send me updated file contents.")
        sys.exit(1)


if __name__ == "__main__":
    main()
