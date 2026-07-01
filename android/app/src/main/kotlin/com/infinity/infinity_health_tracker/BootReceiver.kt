package com.infinity.infinity_health_tracker

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.dexterous.flutterlocalnotifications.ScheduledNotificationBootReceiver

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Delegate to the plugin's built-in boot receiver, which reads all
        // previously scheduled notifications from SharedPreferences and
        // re-registers them with AlarmManager after a device reboot.
        ScheduledNotificationBootReceiver().onReceive(context, intent)
    }
}
