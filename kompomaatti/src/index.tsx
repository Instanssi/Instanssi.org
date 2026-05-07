import moment from 'moment';

// FIXME this is easily half the app's build size
import 'moment-timezone';

import 'moment/dist/locale/fi';
import 'moment/dist/locale/en-gb';

import { observer } from 'mobx-react';

import '@fontsource-variable/exo-2';
import './styles/index.scss';

import 'react-toastify/dist/ReactToastify.css';

import React from 'react';
import ReactDOM from 'react-dom';
import {
    BrowserRouter,
    RouteComponentProps,
    withRouter,
} from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { ToastContainer } from 'react-toastify';

import Views from './views';
import {
    Header,
    Footer,
    // Breadcrumbs,
} from 'src/layout';
import globalState from './state';
import { Messages } from './common/Messages';
// import headerImg from './styles/title-logo-96.png';

// Make the Finnish locale less confusing (is 15.10 a date or a time of day?)
moment.updateLocale('fi', {
    longDateFormat: {
        LT: 'HH:mm',
        LTS: 'HH:mm:ss',
        LLL: 'Do MMMM[ta] YYYY, [klo] HH:mm',
        LLLL: 'dddd, Do MMMM[ta] YYYY, [klo] HH:mm',
        lll: 'Do MMM YYYY, [klo] HH:mm',
        llll: 'ddd, Do MMM YYYY, [klo] HH:mm',
    } as any,
});

// Provide build id in the window env
(window as any).BUILD_ID = __BUILD_ID__;

export default class App extends React.Component {
    render() {
        return (
            <BrowserRouter basename="/kompomaatti">
                <ToastContainer draggable={false} hideProgressBar />
                    <div className="container">
                        <Helmet titleTemplate={'Kompomaatti - %s'}>
                            <title>Kompomaatti</title>
                        </Helmet>
                        <div id="top" className="app-wrap">
                            <Header />
                            <main className="p-3">
                                <Messages />
                                {/*<Breadcrumbs />*/}
                                <Views />
                            </main>
                            <Footer />
                        </div>
                        <AutoScrollWR />
                        <UpdateLang />
                    </div>
            </BrowserRouter>
        );
    }
}

/**
 * Update the page-wide language tag to match the active language.
 */
const UpdateLang = observer(() => (
    <Helmet>
        <html lang={globalState.language} />
    </Helmet>
));

/**
 * Scroll to top when the current path changes.
 */
export class AutoScroll extends React.Component<RouteComponentProps<any>> {
    componentDidUpdate(prevProps: RouteComponentProps<any>) {
        const { props } = this;
        if (props.location.pathname !== prevProps.location.pathname) {
            window.scrollTo(0, 0);
        }
    }

    render() {
        return null;
    }
}

const AutoScrollWR = withRouter(AutoScroll);

ReactDOM.render(<App />, document.getElementById('app'));
