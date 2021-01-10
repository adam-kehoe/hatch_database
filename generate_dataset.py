import json
import csv

HEADER = [
    "id",
    "year",
    "month",
    "day",
    "time",
    "location",
    "stateOrProvince",
    "title",
    "description",
    "locale",
    "duration",
    "credibility",
    "locationFlags",
    "longitude",
    "typeOfUfoCraftFlags",
    "aliensMonstersFlags",
    "apparentUfoOccupantActivitiesFlags",
    "placesVisitedAndThingsAffectedFlags",
    "evidenceAndSpecialEffectsFlags",
    "miscellaneousDetailsFlags",
    "latitude",
    "elevation",
    "relativeAltitude",
    "ref",
    "strangeness",
    "miscellaneousFlags",
    "continent",
    "country",
]


def filter_dataset_by_quality(data, strangeness_threshold=8, credibility_threshold=10):
    # credibility has mean 7.547, 90% percentile = 10
    # strangeness has mean 6.594, 90% percentile = 8
    out = []
    for obs in data:
        strangeness = int(obs["strangeness"])
        credibility = int(obs["credibility"])
        if (
            strangeness >= strangeness_threshold
            and credibility >= credibility_threshold
        ):
            out.append(obs)
    return out


def filter_dataset_by_code(data, code="Nuclear"):
    out = []
    flags = [
        "locationFlags",
        "typeOfUfoCraftFlags",
        "aliensMonstersFlags",
        "apparentUfoOccupantActivitiesFlags",
        "placesVisitedAndThingsAffectedFlags",
        "evidenceAndSpecialEffectsFlags",
        "miscellaneousDetailsFlags",
        "miscellaneousFlags",
    ]
    for obs in data:
        for flag in flags:
            if code in obs[flag]:
                out.append(obs)
    return out


def frequency_by_year(data):
    years = {}
    for obs in data:
        string_year = obs["year"]
        # some years have an approximate sign on
        # remove so we can treat year as a number
        if "~" in string_year:
            string_year = string_year.replace("~", "")
        if string_year:
            year = int(string_year)
            inc_year = years.get(year, 0)
            years[year] = inc_year + 1
    return years


def best_k_markdown(data, label, k=5):
    # print a markdown table of the best 5
    ordered = {index: obs["credibility"] for index, obs in enumerate(data)}
    print("LABEL: %s" % label)
    print(
        "| ID | LOCATION | YEAR | MONTH | DAY | CREDIBILITY | STRANGENESS | DESCRIPTION | REFERENCE |"
    )
    print(
        "|----| -------- | ---- | ----- | --- | ----------- | ----------- | ----------- | --------- |"
    )
    for k in sorted(ordered, key=ordered.get, reverse=True)[0:k]:
        observation = data[k]
        fields = [
            "id",
            "location",
            "year",
            "month",
            "day",
            "credibility",
            "strangeness",
            "description",
            "ref",
        ]
        observation["description"] = observation["description"].replace("\n", "")
        row = "|".join(str(observation[i]) for i in fields)
        print("|" + row + "|")


def write_to_csv(data, outname):
    # write dataset itself to csv
    with open(outname, "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(HEADER)
        for obs in data:
            obs["description"] = obs["description"].replace("\n", "")
            obs["credibility"] = int(obs["credibility"])
            obs["strangeness"] = int(obs["strangeness"])
            out_row = [obs[i] for i in HEADER]
            writer.writerow(out_row)


def write_year_frequency(data, outname):
    with open(outname, "w", newline="") as csvfile:
        writer = csv.writer(
            csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(["year", "count"])
        for k in sorted(data.keys()):
            writer.writerow([k, data[k]])


def process_blog_datasets(data):
    # this can be replaced with other tags of interest
    targets = ["Nuclear", "Photos", "Radar", "Conversation", "Submersible"]

    high_credibility_high_strange = filter_dataset_by_quality(data)
    write_to_csv(high_credibility_high_strange, "high_credible_high_strange.csv")
    best_k_markdown(high_credibility_high_strange, "high strange + high credible")

    for target in targets:
        basic_path = target.lower() + ".csv"
        year_path = target.lower() + "_years.csv"

        case_data = filter_dataset_by_code(data, target)
        years_data = frequency_by_year(case_data)

        write_to_csv(case_data, basic_path)
        write_year_frequency(years_data, year_path)

        # convenience code to create markdown tables for the blog
        # print("++++")
        # best_k_markdown(case_data, target, k=10)
        # print("++++")


def extract_tag_count(data, markdown=True):
    flags = [
        "locationFlags",
        "typeOfUfoCraftFlags",
        "aliensMonstersFlags",
        "apparentUfoOccupantActivitiesFlags",
        "placesVisitedAndThingsAffectedFlags",
        "evidenceAndSpecialEffectsFlags",
        "miscellaneousDetailsFlags",
        "miscellaneousFlags",
    ]
    tags = {}
    for obs in data:
        for flag in flags:
            tag_text = obs[flag]
            case_tags = tag_text.split(",")
            for tag in case_tags:
                tag = tag.replace(" ", "")
                if tag:
                    tag_count = tags.get(tag, 0)
                    tags[tag] = tag_count + 1
    if not markdown:
        return tags
    print("| Tag | Count |\n|----|---|")
    for tag in sorted(tags, key=tags.get, reverse=True):
        print("|%s|%d|" % (tag, tags[tag]))


if __name__ == "__main__":
    dataset = "hatch_data.json"
    json_file = open(dataset)
    data = json.load(json_file)
    json_file.close()

    # this function will generate the subset CSVs, and the years data files
    process_blog_datasets(data)

    # this function will print a markdown table of the frequency of each flag/tag type
    # extract_tag_count(data)
