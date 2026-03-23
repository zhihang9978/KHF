package org.telegram.messenger;

import android.content.Context;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Build;
import android.os.Debug;
import android.os.Process;
import android.text.TextUtils;
import android.util.Log;

import androidx.annotation.NonNull;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;

final class ReleaseSecurity {

    private static final String TAG = "ReleaseSecurity";
    private static final String EXPECTED_RELEASE_PACKAGE = "com.rivermint.pulsechat";
    private static final String EXPECTED_RELEASE_CERT_SHA256 =
            "75CCF56BF717F6264CDFC7679A954D2D6CF0A53304A91269C7F00A6776C99B31";

    private static final String[] SUSPICIOUS_PACKAGES = new String[] {
            "de.robv.android.xposed.installer",
            "org.lsposed.manager",
            "com.topjohnwu.magisk",
            "com.saurik.substrate",
            "io.github.vvb2060.magisk"
    };

    private ReleaseSecurity() {
    }

    static void enforceReleaseGuards(@NonNull Context context) {
        if (BuildVars.DEBUG_VERSION || BuildVars.DEBUG_PRIVATE_VERSION || BuildVars.isBetaApp()) {
            return;
        }

        IntegrityResult integrity = verifyReleaseIntegrity(context);
        if (!integrity.ok) {
            Log.e(TAG, "Integrity violation: " + integrity.reason);
            terminateProcess();
            return;
        }

        EnvironmentResult environment = inspectRuntimeEnvironment(context);
        if (environment.suspicious) {
            Log.w(TAG, "Suspicious runtime detected: " + environment.reason);
        }
    }

    private static IntegrityResult verifyReleaseIntegrity(@NonNull Context context) {
        if (!EXPECTED_RELEASE_PACKAGE.equals(context.getPackageName())) {
            return IntegrityResult.fail("unexpected package " + context.getPackageName());
        }
        if (isDebuggable(context)) {
            return IntegrityResult.fail("debuggable release");
        }
        String actualFingerprint = getCurrentSigningSha256(context);
        if (TextUtils.isEmpty(actualFingerprint)) {
            return IntegrityResult.fail("missing signing fingerprint");
        }
        if (!EXPECTED_RELEASE_CERT_SHA256.equalsIgnoreCase(actualFingerprint)) {
            return IntegrityResult.fail("unexpected signing cert " + actualFingerprint);
        }
        return IntegrityResult.ok();
    }

    private static EnvironmentResult inspectRuntimeEnvironment(@NonNull Context context) {
        if (Debug.isDebuggerConnected() || Debug.waitingForDebugger()) {
            return EnvironmentResult.warn("debugger attached");
        }
        String buildTags = Build.TAGS;
        if (!TextUtils.isEmpty(buildTags) && buildTags.contains("test-keys")) {
            return EnvironmentResult.warn("test-keys build");
        }
        if (readTracerPid() > 0) {
            return EnvironmentResult.warn("process traced");
        }
        for (String packageName : SUSPICIOUS_PACKAGES) {
            if (isPackageInstalled(context, packageName)) {
                return EnvironmentResult.warn("suspicious package " + packageName);
            }
        }
        if (new File("/system/xbin/su").exists() || new File("/system/bin/su").exists()) {
            return EnvironmentResult.warn("su binary present");
        }
        return EnvironmentResult.clean();
    }

    private static boolean isDebuggable(@NonNull Context context) {
        return (context.getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0;
    }

    private static boolean isPackageInstalled(@NonNull Context context, @NonNull String packageName) {
        try {
            context.getPackageManager().getPackageInfo(packageName, 0);
            return true;
        } catch (Throwable ignore) {
            return false;
        }
    }

    private static int readTracerPid() {
        try (BufferedReader reader = new BufferedReader(new FileReader("/proc/self/status"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.startsWith("TracerPid:")) {
                    return Integer.parseInt(line.substring("TracerPid:".length()).trim());
                }
            }
        } catch (Throwable ignore) {
        }
        return 0;
    }

    private static String getCurrentSigningSha256(@NonNull Context context) {
        try {
            PackageManager pm = context.getPackageManager();
            PackageInfo packageInfo;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                packageInfo = pm.getPackageInfo(context.getPackageName(), PackageManager.GET_SIGNING_CERTIFICATES);
                if (packageInfo.signingInfo == null) {
                    return "";
                }
                Signature[] signatures = packageInfo.signingInfo.hasMultipleSigners()
                        ? packageInfo.signingInfo.getApkContentsSigners()
                        : packageInfo.signingInfo.getSigningCertificateHistory();
                return signatures.length > 0 ? signatureToSha256(signatures[0]) : "";
            } else {
                packageInfo = pm.getPackageInfo(context.getPackageName(), PackageManager.GET_SIGNATURES);
                return packageInfo.signatures != null && packageInfo.signatures.length > 0
                        ? signatureToSha256(packageInfo.signatures[0]) : "";
            }
        } catch (Throwable ignore) {
            return "";
        }
    }

    private static String signatureToSha256(@NonNull Signature signature) throws Exception {
        CertificateFactory factory = CertificateFactory.getInstance("X509");
        X509Certificate certificate = (X509Certificate) factory.generateCertificate(
                new java.io.ByteArrayInputStream(signature.toByteArray()));
        return Utilities.bytesToHex(Utilities.computeSHA256(certificate.getEncoded()));
    }

    private static void terminateProcess() {
        Process.killProcess(Process.myPid());
        System.exit(0);
    }

    private static final class IntegrityResult {
        final boolean ok;
        final String reason;

        private IntegrityResult(boolean ok, String reason) {
            this.ok = ok;
            this.reason = reason;
        }

        static IntegrityResult ok() {
            return new IntegrityResult(true, "");
        }

        static IntegrityResult fail(String reason) {
            return new IntegrityResult(false, reason);
        }
    }

    private static final class EnvironmentResult {
        final boolean suspicious;
        final String reason;

        private EnvironmentResult(boolean suspicious, String reason) {
            this.suspicious = suspicious;
            this.reason = reason;
        }

        static EnvironmentResult clean() {
            return new EnvironmentResult(false, "");
        }

        static EnvironmentResult warn(String reason) {
            return new EnvironmentResult(true, reason);
        }
    }
}
