function bind(scope, fn) {
   return function() {
      return fn.apply(scope, arguments);
   }
}

class WaveWidget {
    constructor(list_audios) {
        this.list_audios = list_audios;

        this.waveform_container = document.getElementById('waveform');
        this.slider = document.getElementById('slider');
        this.play_button = document.getElementById("playButton");
        this.stop_button = document.getElementById("stopButton");

        this.ws = WaveSurfer.create({
            container: this.waveform_container,
            waveColor: 'blue',
            progressColor: 'black',
            // height: 100,
            plugins: [
                WaveSurfer.Timeline.create({
                    container: '#wave-timeline',
                    secondaryLabelOpacity: 1.0,
                    primaryLabelInterval: 1.0,
                    secondaryLabelInterval: 0.5
                }),
            ]
        });

        this.ws_regions = this.ws.registerPlugin(WaveSurfer.Regions.create());

        // Initialise for the first sample to be loaded
        this.ws.on('ready', bind(this, this.waveSurferReadyHook));

        noUiSlider.create(this.slider, {
            start: [0, 1],
            connect: true,
            range: {
                'min': 0,
                'max': 1
            },
            step: 0.1
        });

        this.cur_selected_audio_btn = null;
        this.cur_selected_sample_idx = null;
        this.active_region = null;

        this.monitor_handler = async (action, value, sample_id) => {
            const body = {
                "sample_id": sample_id,
                "info_type": action,
                "info_value": value
            }
            // FIXME: the URL needs to be generalised (both base part & stage part)
            const response = await fetch('http://0.0.0.0:8080/stage/test/core/monitor', {
                method: 'POST',
                body: JSON.stringify(body),
                headers: {
                    'Content-Type': 'application/json'
                }
            });
        }
    }

    waveSurferReadyHook() {
        const maxDuration = this.ws.getDuration();

        // Reset the slider range and step
        this.slider.noUiSlider.updateOptions({
            range: {
                'min': 0,
                'max': maxDuration
            },
            step: 0.1
        });

        // Reset the slider values
        this.slider.noUiSlider.set([0, maxDuration]);

        // Delete region if existing and in all cases create a new one (FIXME: this should not be necessary!)
        if (this.active_region) {
            this.active_region.remove()
        }
        this.active_region = this.ws_regions.addRegion({
            start: 0.0,
            end: maxDuration,
            color: 'rgba(154, 219, 246, 0.5)',
            drag: false,
            resize: false
        });

        //
        this.slider.noUiSlider.on("set", bind(this, this.sliderSet));
        this.slider.noUiSlider.on("slide", bind(this, this.sliderUpdate));
    }

    selectSample(index) {
        // Indicate to the server the information about the pause
        var values = this.slider.noUiSlider.get();
        var startTime = parseFloat(values[0]).toFixed(3);
        var endTime = parseFloat(values[1]).toFixed(3);

        if (this.cur_selected_sample_idx) {
            this.monitor_handler("switch_sample", `${this.list_audios[index][0]}`, this.list_audios[this.cur_selected_sample_idx][0]);
        }

        // First disconnect everything
        this.slider.noUiSlider.off("set", this.sliderSet);
        this.slider.noUiSlider.off("slide", this.sliderUpdate);

        // Load the wav
        this.ws.load(this.list_audios[index][1]);

        // Update button to reflect the new status
        if (this.cur_selected_audio_btn) {
            this.cur_selected_audio_btn.disabled = false;
            this.cur_selected_audio_btn.classList.replace("btn-solo", "btn-mute");
        }

        this.cur_selected_audio_btn = document.getElementById("audio_" + index);
        this.cur_selected_audio_btn.disabled = true;
        this.cur_selected_audio_btn.classList.replace("btn-mute", "btn-solo");

        // Reset the time and indicate which new sample is selected
        this.ws.setTime(0);
        this.cur_selected_sample_idx = index;
    }


    stopAudio() {
        // Pause the audio
        this.ws.pause();

        // Indicate to the server the information about the pause
        var values = this.slider.noUiSlider.get();
        var startTime = parseFloat(values[0]).toFixed(3);
        var endTime = parseFloat(values[1]).toFixed(3);
        this.monitor_handler("stop", `[${startTime}, ${this.ws.getCurrentTime()}, ${endTime}]`, this.list_audios[this.cur_selected_sample_idx][0]);

        // Reset everything to authorize replay
        this.ws.setTime(this.active_region.start);
        this.play_button.disabled = false;
        this.stop_button.disabled = true;
    }

    playAudio() {
        var values = this.slider.noUiSlider.get();
        var startTime = parseFloat(values[0]).toFixed(3);
        var endTime = parseFloat(values[1]).toFixed(3);

        this.monitor_handler("play", `[${startTime}, ${endTime}]`, this.list_audios[this.cur_selected_sample_idx][0]);
        if (startTime >= endTime) {
            alert('Start time must be less than end time.');
            return;
        }

        this.active_region.play();
        playButton.disabled = true;
        stopButton.disabled = false;

        const checkTime = () => {
            if (this.ws.getCurrentTime() >= endTime) {
                this.ws.pause();
                this.ws.un('audioprocess', checkTime);

                this.play_button.disabled = false;
                this.stop_button.disabled = true;
            }
        };

        this.ws.on('audioprocess', checkTime);
    }

    sliderUpdate(values, handle, unencoded, tap, positions, noUiSlider) {
        var values = this.slider.noUiSlider.get();
        var startTime = parseFloat(values[0]).toFixed(3);
        var endTime = parseFloat(values[1]).toFixed(3);

        // Reset time
        this.ws.setTime(startTime)

        // Reset region
        this.active_region.setOptions({
            start: startTime,
            end: endTime,
            color: 'rgba(154, 219, 246, 0.5)',
            drag: false,
            resize: false
        });
    }


    sliderSet(values, handle, unencoded, tap, positions, noUiSlider) {
        // First update the region and wavesurfer
        this.sliderUpdate(values, handle, unencoded, tap, positions, noUiSlider);

        // Now, we can send the signal to the monitoring
        var boundaries = `[${values[0]}, ${values[1]}]`;
        this.monitor_handler("set_region", boundaries, this.list_audios[this.cur_selected_sample_idx][0])
    }
}
