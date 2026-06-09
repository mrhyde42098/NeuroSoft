import React, { Component } from "react";
import ErrorBoundary from "./ErrorBoundary.jsx";

/** Error boundary por feature — aísla fallos de rutas lazy. */
export default class RouteErrorBoundary extends Component {
  render() {
    const { feature, children } = this.props;
    return (
      <ErrorBoundary feature={feature}>
        {children}
      </ErrorBoundary>
    );
  }
}
