from eth2spec.phase0.spec import *
from typing import Optional
from eth2.models.lighthouse import Eth2API
from eth2.core import ContentType
from eth2.providers.http import Eth2HttpClient, Eth2HttpOptions
import trio
import httpx

timeout = httpx.Timeout(connect_timeout=25.0,
                        read_timeout=30.0,
                        write_timeout=5.0,
                        pool_timeout=10.0)

# Protected API, use your own :^)
eth2_rpc = 'http://ec2-3-236-142-211.compute-1.amazonaws.com:4000'


async def fetch_state(output_name: str, slot: Optional[Slot]):

    async with Eth2HttpClient(options=Eth2HttpOptions(
            api_base_url=eth2_rpc,
            default_req_type=ContentType.json,
            default_resp_type=ContentType.ssz,
            default_timeout=timeout)) as prov:
        api = prov.extended_api(Eth2API)

        if slot is None:
            head_info = await api.beacon.head()
            slot = head_info.slot
        print(f'fetching state at slot {slot}')

        api_state = await api.beacon.state(slot=slot)

        # Adding annotation explicitly here so you learn the API: lighthouse wraps their objects with extra info.
        state: BeaconState = api_state.beacon_state

        with open(output_name, 'wb') as f:
            state.serialize(f)

        print('done!')

slot = Slot(61060)
slot = compute_start_slot_at_epoch(compute_epoch_at_slot(slot) + 1)
trio.run(fetch_state, 'my_state.ssz', slot)
