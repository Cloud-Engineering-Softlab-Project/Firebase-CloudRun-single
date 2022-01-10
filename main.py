import os

import configuration
app = configuration.init()

from resources.energy_data import EnergyData, ReferenceZones
from resources.testing import HardSleep, SoftSleep

configuration.api.add_resource(EnergyData, '/energy_data')
configuration.api.add_resource(ReferenceZones, '/ref_zones')

configuration.api.add_resource(HardSleep, '/testing/hard_sleep')
configuration.api.add_resource(SoftSleep, '/testing/soft_sleep')

# xray_recorder.configure(service='Energy APIs')
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT")), threaded=True)
