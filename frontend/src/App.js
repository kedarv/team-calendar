
import React from "react";
import "./App.css";
import FullCalendar from "@fullcalendar/react";
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import eventData from "./generated_data/events.json";
import resourceData from "./generated_data/resources.json";

export default class App extends React.Component {
  calendarRef = React.createRef();
  render() {
    return (
      <div id="calendar">
        <FullCalendar
          ref={this.calendarRef}
          plugins={[resourceTimelinePlugin]}
          resources={resourceData}
          events={eventData}
          defaultView={"resourceTimelineYear"}
          height={"auto"}
          resourceLabelText={"People"}
          aspectRatio={1.8}
          editable={false}
          header={{
            left: "today prev,next",
            center: "",
            right: "resourceTimelineDay,resourceTimelineYear"
          }}
          schedulerLicenseKey={"GPL-My-Project-Is-Open-Source"}
        />
      </div>
    );
  }

  componentDidMount() {
    const calendar = this.calendarRef.current.getApi();
    const now = new Date();
    const rangeStart = calendar.state.dateProfile.renderRange.start;
    calendar.scrollToTime(now - rangeStart - 300000000);
  }
}
