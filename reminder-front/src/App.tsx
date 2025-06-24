import React, {useEffect, useState} from 'react';
import './App.css';
import AuthPage from "./components/pages/AuthPage/AuthPage";
import Dashboard from "./components/pages/Dashboard/Dashboard";

function App() {
    const [isAuthed, setIsAuthed] = useState<boolean>(false);

    useEffect(() => {
        if (localStorage.getItem('access_token')) {
            setIsAuthed(true);
        }
    }, []);

    return (
        <div className="App">
            {isAuthed ? <Dashboard/> : <AuthPage setIsAuthed={setIsAuthed}/>}
        </div>
    );



}

export default App;
