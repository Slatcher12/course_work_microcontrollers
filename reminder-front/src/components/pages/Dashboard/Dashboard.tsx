import React, {FC, useEffect, useState} from 'react';
import './Header.scss';
import './Dashboard.scss';
import PopUpModalWindow from "../../common/PopUpModalWindow/PopUpModalWindow";
import Loader from "../../common/Loader/Loader";
import { TimePicker } from 'rsuite';
import 'rsuite/TimePicker/styles/index.css';
import {CalendarDate, IReminder, IDevice} from "../../../interfaces/common";
import DeviceService from "../../../services/DeviceService";
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import {formatCalendarDate} from "../../../utils/common";
import ReminderService from "../../../services/ReminderService";




const Dashboard: FC = () => {
    const [loading, setLoading] = useState<boolean>(false);
    const [isDeviceModalOpen, setIsDeviceModalOpen] = useState(false)
    const [isAlarmModalOpen, setIsAlarmModalOpen] = useState(false)
    const [devices, setDevices] = useState<IDevice[]>([]);
    const [alarms, setAlarms] = useState<IReminder[]>([]);
    const [date, setDate] = useState<CalendarDate>(new Date());

    const [selectedTime, setSelectedTime] = useState(new Date());
    const [userMessage, setUserMessage] = useState('Salam aleikum');



    const fetchDevice = async () => {
        setLoading(true);
        try {
            const devicesData = await DeviceService.getDevices();
            setDevices(devicesData)
        } catch (error) {
            console.error('Error fetching device:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchAlarmsByDate = async (selectedDate: CalendarDate) => {
        setLoading(true);
        console.log('fetching alarms for date:', selectedDate);

        const formattedDate: Date | null = Array.isArray(date) ? date[0] : date;

        if (!formattedDate) {
            setAlarms([]);
            setLoading(false);
            return;
        }

        const dateString = formattedDate.toISOString().split('T')[0]; // Format date as YYYY-MM-DD
        try {
            const alarmsData = await ReminderService.getRemindersByDate(dateString);
            setAlarms(alarmsData);
        }
        catch (error) {
            console.error('Error fetching alarms:', error);
        } finally {
            setLoading(false);
        }

    }

    const handleCreateAlarm = async () => {
        setLoading(true);
        const formattedDate: Date | null = Array.isArray(date) ? date[0] : date;

        if (!formattedDate || !selectedTime) {
            setLoading(false);
            return;
        }

        // Об'єднуємо дату та час в UTC
        const combinedDate = new Date(Date.UTC(
            formattedDate.getFullYear(),
            formattedDate.getMonth(),
            formattedDate.getDate(),
            selectedTime.getHours(),
            selectedTime.getMinutes(),
            selectedTime.getSeconds(),
            selectedTime.getMilliseconds()
        ));

        const dateString = combinedDate.toISOString().split('T')[0]; // "YYYY-MM-DD"
        const timeString = combinedDate.toISOString().split('T')[1]; // "HH:mm:ss.SSSZ"

        try {
            await ReminderService.addReminder({
                time_: timeString,       // ✅ "09:08:55.208Z"
                date_: dateString,       // ✅ "2025-06-13"
                message_: userMessage  // ✅ правильне поле
            } );

            setIsAlarmModalOpen(false);
            fetchAlarmsByDate(formattedDate).then();
        } catch (error) {
            console.error('Error creating alarm:', error);
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        fetchDevice().then();
    }, []);

    useEffect(() => {

        fetchAlarmsByDate(date).then();
    }, [date]);

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('username');
        window.location.href = '/';
    };


    return (
        <>
            <header>
                <h2>Welcome, <span>{localStorage.getItem('username')}</span></h2>
                <button onClick={handleLogout}>Logout</button>
            </header>
            <main className='dashboard'>
                <h1>Dashboard</h1>
                <h2>My device:</h2>
                <div className={'devices-wrapper'}>
                    <div className={'device-item'}>
                        <span>ID</span>
                        <span>Model</span>
                        <span>Serial Number</span>
                        <span>Secret</span>
                        <span
                            className={'button'}
                            onClick={() => setIsDeviceModalOpen(true)}
                        >Add Device</span>

                    </div>
                    {devices.map((device: IDevice) => (
                        <div className='device-item' key={device.id}>
                            <p>{device.id}</p>
                            <p>{device.model}</p>
                            <p>{device.serial_number}</p>
                            <p>{device.secret}</p>
                            <button
                                onClick={async () => {
                                    setLoading(true);
                                    try {
                                        await DeviceService.deleteDevice(device.id?.toString()??'');
                                        fetchDevice().then();
                                    } catch (error) {
                                        console.error('Error deleting device:', error);
                                    } finally {
                                        setLoading(false);
                                    }
                                }}

                            >Delete Device</button>
                        </div>
                    ))}

                </div>
                <div className={'alarm-wrapper'}>
                    <Calendar
                        value={date}
                        onChange={setDate}
                        minDate={new Date()}
                    />

                    <div className={'alarms-container'}>
                        <div className={'title'}>
                            <p>{formatCalendarDate(date)}</p>
                            <button
                                className={'button'}
                                onClick={() => {
                                    ReminderService.deleteExpiredReminders().then(r => {
                                        console.log(r.data);
                                        fetchAlarmsByDate(date).then()
                                    })

                                }}
                            >
                                Delete reminders
                            </button>
                            <button
                                className={'button'}
                                onClick={() => setIsAlarmModalOpen(true)}
                            >Add reminder</button>
                        </div>
                        <div className="alarms-list">
                            {alarms.length === 0 ? (
                                <p className="empty-message">No reminders for this date.</p>
                            ) : (
                                alarms.map((alarm) => (
                                    <div className="alarm-item" key={alarm.id}>
                                        <div className="alarm-info">
                                            <p><strong>Time:</strong> {alarm.time_.slice(0, 5)}</p>
                                            <p><strong>Message:</strong> {alarm.message_}</p>
                                        </div>
                                        <button
                                            className="delete-alarm"
                                            onClick={async () => {
                                                setLoading(true);
                                                try {
                                                    await ReminderService.deleteReminder(alarm.id??'');
                                                    fetchAlarmsByDate(date).then(); // оновити список
                                                } catch (err) {
                                                    console.error("Failed to delete alarm:", err);
                                                } finally {
                                                    setLoading(false);
                                                }
                                            }}
                                        >
                                            ✖
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>




                    </div>
                </div>


                {/*<button className='upload-btn' type='submit'>Upload</button>*/}


                <PopUpModalWindow
                    headText={'Enter device info below'}
                    description={''}
                    active={isDeviceModalOpen}
                    setActive={setIsDeviceModalOpen}

                >
                    <form className={'device-modal'}>
                        <div className='form-group'>
                            <label htmlFor="model">Model:</label>
                            <input type="text" id="model" name="model" required/>
                        </div>
                        <div className='form-group'>
                            <label htmlFor="serial_number">Serial Number:</label>
                            <input type="text" id="serial_number" name="serial_number" required/>
                        </div>
                        <div className='form-group'>
                            <label htmlFor="secret">Secret:</label>
                            <input type="text" id="secret" name="secret" required/>
                        </div>
                        <button
                            type='submit'
                            onClick={async (e) => {
                                e.preventDefault();
                                const form = (e.currentTarget as HTMLButtonElement).closest('form') as HTMLFormElement;
                                if (!form) return;

                                setLoading(true);
                                const model = (form.elements.namedItem('model') as HTMLInputElement).value;
                                const serialNumber = (form.elements.namedItem('serial_number') as HTMLInputElement).value;
                                const secret = (form.elements.namedItem('secret') as HTMLInputElement).value;

                                try {
                                    await DeviceService.addDevice({
                                        model,
                                        serial_number: serialNumber,
                                        secret
                                    });

                                    await DeviceService.bindUser(serialNumber, secret);
                                    setIsDeviceModalOpen(false);
                                    fetchDevice().then();
                                } catch (error) {
                                    console.error('Error adding device:', error);
                                } finally {
                                    setLoading(false);
                                }
                            }}
                        >Add Device</button>
                    </form>




                </PopUpModalWindow>
                <PopUpModalWindow
                    headText={'Choose time and melody for alarm'}
                    description={''}
                    active={isAlarmModalOpen}
                    setActive={setIsAlarmModalOpen}
                >
                    <TimePicker
                        format="HH:mm"
                        defaultValue={selectedTime}
                        onChange={(value) => setSelectedTime(value ?? new Date())}
                    />
                    <input value={userMessage} onChange={(e) => setUserMessage(e.target.value)} />

                    <button
                        className={'upload-btn'}
                        style={{marginTop: '20px'}}
                        onClick={() => handleCreateAlarm()
                    }>Create alarm</button>

                </PopUpModalWindow>
                {loading&&<Loader/>}

            </main>

        </>
    );
};

export default Dashboard;