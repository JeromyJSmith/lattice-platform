# Improve Front End UX of IsoSpeedBench

UPDATE src/pages/IsoSpeedBench.vue, src/components/IsoSpeedBenchRow.vue:

    ADD a settings button to the right of reset.

        when we click settings we show content to the right of it in a flex row.

    Replace the 'speed' setting with a 'speed' slider and move it into the settings.
    
    Add a setting 'scale' its a slider that controls the size of the blocks. min 20 max 150. 

        Be sure this updates IsoSpeedBenchRow.vue to use the new scale.

    Add a setting 'model stat detail' its a single select with 'verbose' | 'simple' | 'hide'.
        'verbose' - current version
        'simple' - show only accuracy and avg tps
        'hide' - hide all model stats only show the model name

        place this in the settings row.