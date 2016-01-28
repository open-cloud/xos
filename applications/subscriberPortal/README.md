# Subscriber Portal

This is a demonstrative implementation of a subscriber portal.
Note that this is intended to demonstrate a possible implementation, but it is not the only way.

This demo is developed with AngularJs, but your subscriber portal could be developed using whichever framework 
in whichever language as it should only integrate XOS api with your services (eg: Authentication, CRM, Bug Tracker...)
 
## Concept Demonstrated

This is intended to be a portal for a Subscriber user to manage a Parent Control Application provided by XOS.
To Subscriber will be able to choose between two bundles:
 - Basic Bundle
 - Family Bundle
 
The subscriber should enable the _Family Bundle_ trough the _Bundles_ page.
Once enable he will be able to define different levels of Parental Control for each device in his house.

### Data Sources

_Bundles_ are intended as a group of services offered by a company, so they should be managed by the company services and business logic.
They are not intended to be part of XOS, so for demonstrative purposes have been hardcoded into the application.
Consider that this kind of information can be provided by a remote service.

_Subscribers_, _Users_ and _Parental Control_ are information managed by XOS and currently provided by its API. 

## Getting started

_All commands in this section refers to `applications/subscriberPortal`_

_Note that NodeJs and Bower are required to run this demo_

To open this demo:

 - open `env/default.js` and replace `host` with the URL of your XOS installation.
 - from the portal root execute `npm start`

This should open the demo in the browser.

### Bugs

Please report any bug or question trough github issues.
