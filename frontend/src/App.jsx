import { Provider } from 'react-redux';
import { store } from './app/store';
import FormPanel from './components/FormPanel/FormPanel';
import ChatPanel from './components/ChatPanel/ChatPanel';

export default function App() {
  return (
    <Provider store={store}>
      <div className="app-container">
        <FormPanel />
        <ChatPanel />
      </div>
    </Provider>
  );
}
