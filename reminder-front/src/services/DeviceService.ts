import $api from "../http";
import {IDevice} from "../interfaces/common";



export default class DeviceService {
    static async getDevices(): Promise<IDevice[]> {
        return $api.get<IDevice[]>('/devices').then(response => response.data);
    }

    static async addDevice(device: IDevice) {
        return $api.post(
            `/devices`,
            {
                model: device.model,
                serial_number: device.serial_number,
                secret: device.secret
            })

    }

    static async deleteDevice(deviceId: string) {
        return $api.delete(`/devices/${deviceId}`)
    }

    static async bindUser(serial_number:string, secret_code: string) {
        return $api.post(
            `/devices/user`,
            {},
            {
                headers: {"X-DEVICE-TOKEN": `${serial_number}:${secret_code}`}
            }
            )

    }



}
