import React from "react";
import "./App.css";
import FullCalendar from "@fullcalendar/react";
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import eventData from "./generated_data/events.json";
import resourceData from "./generated_data/resources.json";
import ReactTooltip from 'react-tooltip';
import interactionPlugin from "@fullcalendar/interaction";

export default class App extends React.Component {
  calendarRef = React.createRef();
  render() {
    return (
      <div id="calendar">
        <FullCalendar
          ref={this.calendarRef}
          plugins={[resourceTimelinePlugin, interactionPlugin]}
          resources={resourceData}
          events={eventData}
          defaultView={"resourceTimelineMonth"}
          height={"auto"}
          scrollTime={"09:00"}
          businessHours={{
            daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
            startTime: "09:00",
            endTime: "18:00"
          }}
          resourceLabelText={"People"}
          aspectRatio={1.8}
          editable={false}
          header={{
            left: "today prev,next",
            center: "title",
            right:
              "resourceTimelineDay,resourceTimelineMonth,resourceTimelineYear"
          }}
          eventPositioned={this.handleEventPositioned}
          schedulerLicenseKey={"GPL-My-Project-Is-Open-Source"}
        />
        <ReactTooltip place="top" type="dark" effect="float"/>
      </div>
    );
  }

  componentDidMount() {
    const calendar = this.calendarRef.current.getApi();
    const now = new Date();
    const rangeStart = calendar.state.dateProfile.renderRange.start;
    calendar.scrollToTime(now - rangeStart - 300000000);
  }

  handleEventPositioned(info) {
    const resource = info.event.getResources()[0].title;
    info.el.setAttribute("data-tip", resource + ' ' + info.event.title);
     ReactTooltip.rebuild();
   }
}
