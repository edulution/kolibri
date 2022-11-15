Feature: Super admin explores other libraries

  Background:
    Given I am signed in as a super admin
    	And I am connected to the internet and to other devices on the network
			And I am at *Learn > Library*
			And there are imported channels with resources on the device

	Scenario: Explore someone else's library
		When I load the *Learn > Library* page
			And I look at a library in the *Other libraries* section of the page
			And I click the *Explore this library* card
		Then I see the *Explore libraries* page
			And I see the search by keyword and the search filters to the left
			And I see a *All libraries* link at the top
			And I see a *Library of '<device>'* label
			And I see all the available channels for the selected library
		When I click on a channel
		Then I am at the *Browse channel* modal
			And I can see all of the available resources

	Scenario: Go to explore *All libraries* page
		Given there are at least 4 other libraries and at least 1 is pinned
		When I look at the *Other libraries* section of the page
		Then I see there only channels for pinned libraries
			And I see a *More libraries* section under the *Other libraries* section
			And I see some of the unpinned libraries
			And I see a *See all libraries* card
		When I click the *See all libraries* card
		Then I see the *All libraries* page
			And I see a *All libraries* label
			And I see *Showing the libraries on other devices and networks around you* below the *All libraries* label
			And I see the *Kolibri content library* at the top
			And I see the available unpinned full devices #TO DO needs clarification whether we see the pinned devices too
			And I see the available learn-only devices
			And I see the *External storage* section
			And I see an *Explore* button next to each section

	Scenario: Pin a library
		Given I am at the *All libraries* page
		When I click the pin icon next to a unpinned library
		Then the color of the icon is changed to black
		When I close the *Explore library* page
		Then I am back at the *Library* page
			And I can see the newly pinned library

	Scenario: Remove pin from a library
		Given I am at the *All libraries* page
		When I click the pin icon next to a pinned library
		Then the color of the icon is changed to white
		When I close the *Explore library* page
		Then I am back at the *Library* page
			And I can see the that the unpinned library is no longer displayed there

	Scenario: Show other learn-only devices under "More libraries"
		Given I am at the *All libraries* page
			And there are available learn-only devices
		When I scroll down to the *More libraries* section
			And I click the *Show* button
		Then I see a section for each available learn-only device
			And for each section I see the name of the learn-only device *Learn-only device 1 name*
			And I see a pin icon to the right of the name
			And I see an *Explore* button to the further right
			And I see the channel cards
			And I see a *Version X* text at the bottom left corner of each card
		When there are multiple available learn-only devices
		Then I see a *Show more* button under the displayed learn-only devices
		When I click the *Show more* button
		Then I see another set of learn-only devices
