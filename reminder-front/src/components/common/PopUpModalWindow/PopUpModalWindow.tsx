import React, {Dispatch, FC, SetStateAction} from 'react';
import './PopUpModalWindow.scss'
import close from "./close.svg"

interface PopUpModalWindowProps {
    headText: string,
    description: string,
    active:boolean,
    setActive:Dispatch<SetStateAction<boolean>>,
    children:React.ReactNode
}

const PopUpModalWindow: FC<PopUpModalWindowProps> = (
    {headText, description, active, setActive, children}

) => {
    return (
        <div className={`popup-modal ${active&&'active'}`} onClick={() => setActive(false)}>
            <div className={`popup-modal-content ${active&&'active'}`} onClick={e => e.stopPropagation()}>
                <div>
                    <div className='popup-head'>
                        <div>
                            <h3>{headText}</h3>
                            <h4>{description}</h4>
                        </div>
                        <img src={close} alt={'close'} onClick={() => setActive(false)}/>
                    </div>
                    {children}
                </div>
            </div>
        </div>
    );
};

export default PopUpModalWindow;