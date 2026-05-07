import React from 'react';
import L from '../L';

export default class ErrorBoundary extends React.Component<{
    children: any;
}> {
    state = {
        error: null as null | Error,
        errorInfo: null as null | React.ErrorInfo,
    };

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        this.setState({ error, errorInfo });
    }

    reset = () => {
        this.setState({
            error: null,
            errorInfo: null,
        });
    }

    render() {
        const { error, errorInfo } = this.state;

        if (error) {
            let errorText: string;
            let errorInfoText: string;
            try {
                const { name, message, stack } = error;
                errorText = JSON.stringify({ name, message, stack }, null, 4);
            } catch (error) {
                errorText = '(unknown error)';
            }
            try {
                errorInfoText = JSON.stringify(errorInfo && errorInfo.componentStack, null, 4);
            } catch (error) {
                errorInfoText = '(no info)';
            }
            return (
                <div>
                    <h2><L text="error.title" /></h2>
                    <p><L text="error.text" /></p>
                    <pre>
                        {errorText}
                    </pre>
                    <pre>
                        {errorInfoText}
                    </pre>
                    <button
                        className="btn btn-primary"
                        type="button"
                        onClick={this.reset}
                    >
                        <span className="fa fa-random" />
                        &ensp;
                        <L text="error.retry" />
                    </button>
                </div>
            );
        }

        return this.props.children;
    }
}
