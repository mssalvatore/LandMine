import time

class AlertDeduplicator:
    def __init__(self, alert_threshold, alert_threshold_window_sec, suppress_duplicate_alerts):
        self.alert_threshold = alert_threshold
        self.alert_threshold_window_sec = alert_threshold_window_sec
        self.suppress_duplicate_alerts = suppress_duplicate_alerts
        self.recent_alerts = dict()
        self.last_sent_count = 0
        self.last_sent_time = 0

    def should_send_new_alert(self, snort_alert, current_time=None):
        current_time = time.time() if current_time is None else current_time

        if self._threshold_window_exceeded(current_time, self.last_sent_time):
            self._clear_state()

        if self.last_sent_count >= self.alert_threshold:
            return False

        if self._should_suppress_duplicate_alert(snort_alert, current_time):
            return False

        self.last_sent_count += 1
        self.last_sent_time = current_time
        return True

    def _threshold_window_exceeded(self, current_time, last_sent_time):
        return (current_time - self.alert_threshold_window_sec) > last_sent_time

    def _clear_state(self):
        self.last_sent_count = 0
        self.recent_alerts.clear()

    def _should_suppress_duplicate_alert(self, snort_alert, current_time):
        if not self.suppress_duplicate_alerts:
            return False

        snort_alert_key = AlertDeduplicator._snort_alert_to_dict_key(snort_alert)
        last_sent_alert_time = self.recent_alerts.get(snort_alert_key, 0)
        if not self._threshold_window_exceeded(current_time, last_sent_alert_time):
            return True

        self.recent_alerts[snort_alert_key] = current_time
        return False

    @staticmethod
    def _snort_alert_to_dict_key(snort_alert):
        # Strip timestamp from snort alert text as it is misleading when
        # identifying duplicate alerts
        snort_alert_txt = str(snort_alert)
        snort_alert_lines = snort_alert_txt.split('\n')
        return "\n".join(snort_alert_lines[1:])
