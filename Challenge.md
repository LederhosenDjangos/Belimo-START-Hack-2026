# Belimo Case Development Framework

## Topic of the Case
**Smart Actuators**

## Title of the Case
**Unlocking Insights from Belimo Actuator Data for Smart Building Solutions**

## Case Summary
Belimo’s actuators collect and measure a large amount of internal data, including valuable information about how they are operated, such as load profiles and control parameters. Today, these datapoints are not yet used to create additional value for customers.

The goal of this case is to create innovative concepts by analyzing signals from Belimo’s field devices, such as torque, motor position, and temperature, to generate actionable insights. These insights should help resolve issues, correct errors, improve energy efficiency in control systems, and create measurable value during installation, commissioning, and operation.

### Target Users
- Installers
- Mechanical contractors
- System integrators
- OEMs
- Facility managers

These users operate in the HVAC industry for commercial buildings.

## Data

### Hardware
A range of Belimo products will be available on site for interactive use. Participants can engage directly with the devices, generate data and measurements, and observe the outcomes.

### Available Data
Live actuator signals are available through InfluxDB, including:
- Torque
- Motor position feedback
- Embedded temperature
- Other device metrics

### Additional Helpful Data Sources
Potentially useful additional sources may include:
- Historical actuator behavior patterns
- Building system context
- Installation and commissioning records
- Environmental operating conditions

## Technology

### Hardware Setup
Belimo actuators stream data to InfluxDB hosted on Raspberry Pi devices. This setup abstracts away all non-common interfaces, making it easier for participants to access and work with the data.

Participants are encouraged to interact freely with the valves and actuators to explore the available signals.

### Software Setup
- InfluxDB server instance running on Raspberry Pi
- Time-series data access via standard InfluxDB client libraries
- Direct access available when connected to the same network as the Raspberry Pi
- Writing to the database causes the actuator to move

## Use Case and Business Case
Teams must propose a business case that uses actuator-derived insights to create measurable value for customers.

Potential focus areas include:
- Debugging information
- Malfunction detection
- Predictive maintenance
- Energy optimization
- Anomaly detection
- New service models
- Easier installation, commissioning, or embedment support

The proposed business case should clearly demonstrate quantifiable customer benefits enabled through actionable insights generated from actuator data.

## Judgment Criteria

### Creativity (35%)
- New, out-of-the-box ideas for insights that are relevant for customers
- New and innovative approaches or algorithms to compute insights from available actuator data
- Highest recognition goes to approaches and algorithms that generate insights previously unknown or unanticipated

### Presentation (10%)
- Easy to understand why the use case is important and what the solution is
- Captivating storyline
- Professional design is **not** important

### Technical Feasibility (35%)
- Feasibility must be realistic, not just theoretically possible
- Real-world limitations must be considered
- Examples include production variance in predictive maintenance or signal isolation from disturbances

### Business Feasibility (20%)
- Strong fit to the HVAC industry

## Presentation Prototype

### Format
Use a standard and portable presentation format, such as:
- PowerPoint
- PDF
- Similar common presentation formats

### Required Elements
The presentation should include:
- Problem statement
- Solution
- Technical approach
- Business case

### Requirements
The presentation should be:
- Clear
- Concise
- Engaging

## Points of Contact
The following Belimo representatives will be present at the event:

- **Forest Reider** — Research
- **Giulia Zappoli** — Research
- **Dennis Johannesen** — Global Product Management
- **Alexander Egli** — Research
- **Michael Schupp** — Research

## Prize
The winning team receives:

**CHF 3,000 for a team event**
