def enlace_video(ajustes, token):
    if ajustes["video_modo"] == "jitsi":
        return f"https://meet.jit.si/TuEspacio-{token[:16]}"
    return ajustes.get("video_enlace_fijo", "")
