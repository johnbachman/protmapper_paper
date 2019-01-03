import sys
import pickle
from indra.statements import Agent, ModCondition
from indra.sources.biopax import processor as bpc
from indra.sources.biopax import pathway_commons_client as pcc


def save_modified_agents(owl_file, output_file):
    print('Reading %s...' % owl_file)
    model = pcc.owl_to_model(owl_file)
    mf_class = bpc._bpimpl('ModificationFeature')

    objs = model.getObjects().toArray()

    agents = []
    for obj in objs:
        if not isinstance(obj, mf_class):
            continue
        try:
            mc = bpc.BiopaxProcessor._extract_mod_from_feature(obj)
        except Exception as e:
            print('ERROR: ' + str(e))
            continue
        if not mc or not mc.residue or not mc.position:
            continue

        proteins = obj.getFeatureOf().toArray()
        if not proteins:
            continue
        for protein in proteins:
            name = bpc.BiopaxProcessor._get_element_name(protein)
            db_refs = bpc.BiopaxProcessor._get_db_refs(protein)
            agent = Agent(name, mods=[mc], db_refs=db_refs)
            reactions = protein.getParticipantOf().toArray()
            if not reactions:
                upstream = protein.getMemberPhysicalEntityOf().toArray()
                for u in upstream:
                    reactions += u.getParticipantOf().toArray()
            for reaction in reactions:
                controls = reaction.getControlledOf().toArray()
                if not controls:
                    agents.append(agent)
                for contr in controls:
                    agents.append(agent)

    with open(output_file, 'wb') as fh:
        pickle.dump(agents, fh)

if __name__ == '__main__':
    owl_file = sys.argv[1]
    pkl_file = sys.argv[2]
    save_modified_agents(owl_file, pkl_file)
    """
    for db in dbs:
        owl_file = owl_pattern % db
        output_file = 'output/pc_%s_modified_agents.pkl' % db
        save_modified_agents(owl_file, output_file)
    save_modified_agents('data/Kinase_substrates.owl',
                         'output/psp_kinase_substrate_biopax.pkl')
    save_modified_agents('data/reactome/Homo_sapiens.owl',
                         'output/reactome_human.pkl')
    """
