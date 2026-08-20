Meeting summary:

14/8/2026 : 


CDSS Group Meeting Summary — 14 August 2026
Hi everyone,

Thank you all for the great discussion and contributions.

Big Picture
The main goal of the CDSS is to detect problems, suggest next steps, and support clinical decision-making, ultimately contributing to greater mission independence and medical autonomy during long-duration spaceflight.

We also suggested Systems Medicine for Human Spaceflight as an important reference for the group.

A major limitation of many current spaceflight datasets, including several OSDR datasets, is that they are mainly focused on multi-omics and research questions rather than practical longitudinal clinical scenarios. Therefore, we need to build a dedicated synthetic astronaut clinical dataset for development and evaluation of the CDSS.

Astronaut / Patient Simulation
The first major task will be to create realistic longitudinal astronaut profiles.

Each astronaut will have baseline characteristics such as:

Age and sex

Medical history

Anatomy and physiology

Ophthalmic measurements

OCT variables such as RNFL and choroidal thickness

Refraction

Other relevant clinical and mission-related variables

Each simulated astronaut will then be followed across multiple mission timepoints, approximately:

Preflight → Launch → In-flight → Post-flight

For example:

L-30 → L → L+30 → L+90 → L+120

The exact number and timing of measurements should be extracted from the literature. A possible structure may include approximately three preflight, three in-flight, and three post-flight assessments.

For every astronaut, different longitudinal clinical scenarios can then be generated, including:

Normal/stable state

Progressive changes

Persistent/steady abnormalities

Missing modality

Poor-quality data

Incomplete information

Other clinically relevant scenarios

This will create many combinations of astronauts, timepoints, and clinical states for testing the CDSS.

Evidence-Based Simulation Workflow
The simulation should be transparent, reproducible, and evidence-based.

Literature review → Structured spreadsheet → LLM-assisted extraction → Paper-by-paper verification → Simulation → Computational validation → Clinical expert validation

From the literature, we will extract variables such as:

Clinical and physiological variables

Ophthalmic and OCT variables

Demographics

Health conditions

Measurement methods

Normal and abnormal ranges

Longitudinal changes

Relationships between variables

These will first be recorded in a shared spreadsheet.

LLMs such as ChatGPT or Claude can help extract and organize the information, but every extracted value should remain linked to its source and then be rechecked against the original paper. This is important to prevent unsupported or hallucinated values and make the AI-assisted process scientifically reproducible.

After defining variables and ranges, we can compare different methods of patient simulation rather than relying only on simple random generation.

Clinical experts, particularly ophthalmologists for the SANS scenarios, will then assess whether the generated longitudinal cases are realistic and clinically meaningful.

Combining Synthetic and Real Data
We should remain open to using real and analogue datasets.

If we obtain a well-structured clinical dataset, even if incomplete, an important question will be how to combine it with our simulation framework.

Examples include bed-rest studies and other terrestrial spaceflight analogues.

The goal is not to replace real data with simulation, but to use simulation to extend existing datasets, generate missing clinical trajectories, and create rare or difficult-to-observe scenarios.

CDSS Development and Evaluation
The initial scientific question is:

How safely and accurately can a CDSS detect clinical changes and suggest the appropriate next steps during spaceflight?

SANS can be the first focused use case.

Different CDSS approaches can then be compared:

Rule-based systems

LLM-based systems

Hybrid approaches

Other probabilistic or causal methods as the project develops

The same simulated scenarios should be presented to each system, and their outputs compared against expert-defined reference standards using a structured scoring framework.

The longer-term pathway is:

Astronaut simulation → CDSS validation → Software development → Deployment-oriented architecture

The software should eventually consider real mission constraints such as:

Edge computing

Fast response

Limited connectivity

Computing resources

Appropriate programming architecture

Mission independence

The first broader product can become an Eye Triage CDSS, with SANS as one important scenario. The framework could later expand toward other human-system risks such as thrombosis, embolism, renal stones, radiation-related problems, and other classes defined within NASA’s Human System Risk framework.

Collaboration
A shared spreadsheet should be available to interested members so that literature extraction and dataset development can happen collaboratively.

Supervision / Advising: @ElisabethAslinger, @RobertReynolds
Volunteer: Soujanya Pittala

Immediate Next Steps
Collect all relevant papers in one shared folder.

Prepare the structured variable-extraction spreadsheet.

Begin evidence-based extraction of variables, ranges, timepoints, and clinical relationships.

Explore computational methods for validating synthetic patient/astronaut data.

Establish an official CDSS repository within the AWG GitHub for code, data structures, documentation, and version tracking.
